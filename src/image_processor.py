import os
import time
from typing import Dict, List

from PIL import Image, ImageFile
from send2trash import send2trash

from models import ImageProcessorResult
from multi_worker import MultiThreadWorker
from worker_signals import WorkerSignals

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


class ImageProcessor:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir

    def dir_open(self) -> int:
        os.chdir(self.source_dir)
        cnt = 0
        for _, _, files in os.walk(self.source_dir):
            for file in files:
                file = file.lower()
                if file.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                    cnt += 1
        return cnt

    def uncopy(self) -> int:
        def exit_function() -> int:
            try:
                if len(os.listdir(new_dir)) == 0:
                    os.rmdir(new_dir)
                old_pwd = os.getcwd()
                os.chdir(self.source_dir)
                send2trash("DONT DELETE.txt")
                os.chdir(old_pwd)
            except Exception:
                pass
            return self.dir_open()

        new_dir = os.path.join(self.source_dir, "copies")
        if not os.path.isdir(new_dir):
            return exit_function()
        initial_names = {}
        dont_delete_path = os.path.join(self.source_dir, "DONT DELETE.txt")
        if os.path.isfile(dont_delete_path):
            with open(dont_delete_path, "r", encoding="utf-8") as file:
                for line in file:
                    name, path = line.strip().split(" -- ")
                    initial_names[name] = path
        else:
            return exit_function()
        for file in os.listdir(new_dir):
            try:
                os.rename(os.path.join(new_dir, file), initial_names[file])
            except (OSError, KeyError):
                continue
        return exit_function()

    def delete(self, hash_dict: Dict[str, List[str]]) -> int:
        self.uncopy()
        old_pwd = os.getcwd()
        for value in hash_dict.values():
            head = os.path.dirname(value[0])
            os.chdir(head)
            for i in range(len(value) - 1):
                try:
                    send2trash(os.path.basename(value[i]))
                except Exception as e:
                    print(e)
        os.chdir(old_pwd)
        return self.dir_open()

    def find_similar_images(
        self, method: int, threads: int, signals: WorkerSignals
    ) -> ImageProcessorResult:
        worker = MultiThreadWorker(method, threads, self.source_dir, signals)
        hash_dict = worker.get_hash_multithreaded()

        if hash_dict:
            new_dir = os.path.join(self.source_dir, "copies")
            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)
        signals.progress.emit(100, "Finishing up...")
        j = 0
        copies_list = []
        for paths in hash_dict.values():
            res = 0
            max_num = 0
            for i, path in enumerate(paths):
                with Image.open(path) as image:
                    tmp = image.width * image.height
                    if tmp > res:
                        res = tmp
                        max_num = i
            paths[-1], paths[max_num] = paths[max_num], paths[-1]
            for i, path in enumerate(paths):
                new_name = f"copy {j}_{i}.{path.split('.')[-1]}"
                new_path = os.path.join(new_dir, new_name)
                if not os.path.isdir(new_path):
                    os.rename(path, new_path)
                    copies_list.append(new_name + " -- " + path + "\n")
            j += 1
        if copies_list:
            with open(
                os.path.join(self.source_dir, "DONT DELETE.txt"), "w", encoding="utf-8"
            ) as file:
                file.writelines(copies_list)

        result = ImageProcessorResult(
            int(100 * (time.time() - signals.started)) / 100,
            j,
            self.dir_open(),
            self.source_dir,
            hash_dict,
        )
        return result
