import os
import threading
import time
from collections import defaultdict
from queue import Queue
import imagehash
import worker
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


class MultyWorker:
    def __init__(self, method, workers, path):
        self.path = path
        self.workers = workers
        self.method = method
        self.hash_dict = defaultdict(list)
        self.lock = threading.Lock()

    def get_hash(self, que, func):
        while True:
            path = que.get()
            if path is None:
                break
            try:
                with Image.open(path) as image:
                    hash = func(image)
                    image.close()

                    if hash is None:
                        continue
                    with self.lock:
                        self.hash_dict[hash].append(path)
            except Exception:
                continue

    def work(self, progress, start_time):
        num = 0
        res = {}
        Len = sum(
            os.path.isfile(f)
            for f in map(lambda x: x.name, os.scandir(self.path))
            if ".png" in f.lower() or ".jpg" in f.lower()
        )
        func_dic = {
            0: imagehash.phash,
            1: imagehash.dhash,
            2: imagehash.average_hash,
            3: imagehash.whash,
            4: imagehash.colorhash,
            5: imagehash.crop_resistant_hash,
        }

        que = Queue(2 * self.workers)

        threads = [
            threading.Thread(
                target=self.get_hash,
                args=(
                    que,
                    func_dic[self.method],
                ),
            )
            for _ in range(self.workers)
        ]

        for thread in threads:
            thread.start()

        with os.scandir(self.path) as it:
            for entry in it:
                if worker.a is True:
                    break
                if entry.is_file():
                    que.put(entry.name)
                    num += 1
                    progress.emit(
                        100 * (num - self.workers * 2) // Len,
                        round(time.time() - start_time, 3),
                    )

        for _ in range(len(threads)):
            que.put(None)

        for thread in threads:
            thread.join()

        for key, value in self.hash_dict.items():
            if len(value) > 1:
                res[key] = value
        return res
