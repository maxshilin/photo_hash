import os
import concurrent.futures
import time
from collections import defaultdict
from typing import Optional, Dict, Callable
from dataclasses import dataclass

import imagehash
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


@dataclass
class HashModel:
    path: str
    image_hash: str


class MultiThreadWorker:
    def __init__(self, method: int, max_workers: int, source_dir: str):
        self.dir = source_dir
        self.max_workers = max_workers
        self.method = method
        self.hash_dict = defaultdict(list)

    @staticmethod
    def get_hash(path: str, func: Callable[..., str]) -> Optional[HashModel]:
        try:
            with Image.open(path) as image:
                image_hash = func(image)
                return HashModel(path, image_hash)
        except Exception:
            return None

    def get_hash_multithreaded(self, progress, start_time: int) -> Dict[str, str]:
        res = {}
        images = []
        for root, _, files in os.walk(self.dir):
            for file in files:
                images.append(os.path.join(root, file))

        func_dic = {
            0: imagehash.phash,
            1: imagehash.dhash,
            2: imagehash.average_hash,
            3: imagehash.whash,
            4: imagehash.colorhash,
            5: imagehash.crop_resistant_hash,
        }

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [
                executor.submit(self.get_hash, path, func_dic[self.method])
                for path in images
            ]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                hash_model = future.result()
                if hash_model:
                    self.hash_dict[hash_model.image_hash].append(hash_model.path)

                progress.emit(
                    100 * i // len(images),
                    round(time.time() - start_time, 3),
                )

        for key, value in self.hash_dict.items():
            if len(value) > 1:
                res[key] = value
        return res
