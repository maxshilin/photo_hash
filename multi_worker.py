import os
import threading
import time
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
        self.hash_dict = {}
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

                    if hash in self.hash_dict:
                        with self.lock:
                            self.hash_dict[hash].append(path)
                    else:
                        with self.lock:
                            self.hash_dict[hash] = [path]
            except Exception:
                continue

    def work(self, progress, start_time):
        res = {}
        images = []
        for root, _, files in os.walk(self.path):
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

        que = Queue(self.workers)

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

        for i, entry in enumerate(images):
            if worker.a is True:
                break

            que.put(entry)
            progress.emit(
                100 * (i - self.workers) // len(images),
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
