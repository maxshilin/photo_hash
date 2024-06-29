import concurrent.futures
import os
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

import imagehash
from PIL import Image, ImageFile

from models import HashResult
from worker_signals import WorkerSignals

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


THREAD_MAPPING: Dict[int, int] = {0: os.cpu_count(), 1: 1, 2: 2, 3: 4, 4: 8}

HASH_FUNCTIONS: Dict[int, Callable[..., Any]] = {
    0: imagehash.phash,
    1: imagehash.dhash,
    2: imagehash.average_hash,
    3: imagehash.whash,
    4: imagehash.colorhash,
    5: imagehash.crop_resistant_hash,
}


class MultiThreadWorker:

    def __init__(
        self, method: int, threads: int, source_dir: str, signals: WorkerSignals
    ):
        self.max_workers: int = THREAD_MAPPING.get(threads, os.cpu_count())
        self.hash_func = HASH_FUNCTIONS.get(method, imagehash.phash)
        self.source_dir = source_dir
        self.signals = signals
        self.hash_dict = defaultdict(list)

    @staticmethod
    def get_hash(path: str, func: Callable[..., str]) -> Optional[HashResult]:
        try:
            with Image.open(path) as image:
                image_hash = func(image)
                return HashResult(path, str(image_hash))
        except Exception:
            return None

    def get_hash_multithreaded(self) -> Dict[str, List[str]]:
        res = {}
        images = []
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                    images.append(os.path.join(root, file))

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [
                executor.submit(self.get_hash, path, self.hash_func) for path in images
            ]
            total_images = len(images)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                hash_model = future.result()
                if hash_model:
                    self.hash_dict[hash_model.image_hash].append(hash_model.path)

                self.signals.emit_progress(i, total_images)

        for key, value in self.hash_dict.items():
            if len(value) > 1:
                res[key] = value
        return res
