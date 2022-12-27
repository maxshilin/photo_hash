import os
from collections import defaultdict
import time
import gc
import concurrent.futures
from PIL import Image, ImageFile
import imagehash
from send2trash import send2trash
import worker

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


class PhotoHash:
    def __init__(self, key, progress, start_time, Len):
        self.num = 0
        self.key = key
        self.progress = progress
        self.time = start_time
        self.Len = Len
        self.func_dic = {
            0: imagehash.phash,
            1: imagehash.dhash,
            2: imagehash.average_hash,
            3: imagehash.whash,
            4: imagehash.colorhash,
            5: imagehash.crop_resistant_hash,
        }

    def hash(self, path):
        self.num += 1
        self.progress.emit(
            100 * self.num // self.Len, round(time.time() - self.time, 3)
        )
        if worker.a is True:
            return None, None
        try:
            with Image.open(path) as im:
                hash = self.func_dic[self.key](im)
                im.close()
        except Exception:
            return None, None

        return str(hash), path


def dir_open(path, signals=0):
    os.chdir(path)
    return sum(
        os.path.isfile(f)
        for f in os.listdir(path)
        if ".png" in f.lower() or ".jpg" in f.lower()
    )


def uncopy(path, signals):
    newdir = os.path.join(path, "copies")
    if os.path.isdir(newdir):
        for file in os.listdir(newdir):
            if "copy " in file:
                new_file = file.replace("copy ", "")
                new_file = new_file[new_file.find(" ") + 1 :]  # noqa E203
                try:
                    os.rename(
                        os.path.join(newdir, file),
                        os.path.join(path, new_file),
                    )
                except OSError:
                    continue
        if len(os.listdir(newdir)) == 0:
            os.rmdir(newdir)
    return dir_open(path)


def delete(arg, signals):
    path = arg[0]
    hash_dict = arg[1]
    newdir = os.path.join(path, "copies")
    os.chdir(newdir)
    if os.path.isdir(newdir):
        if not hash_dict:
            os.chdir(path)
            return uncopy(path, signals)
        for key in hash_dict.keys():
            for i in range(len(hash_dict[key]) - 1):
                send2trash(hash_dict[key][i])
    os.chdir(path)
    return uncopy(path, signals)


def get_hash_dict(path, progress, start_time, method, threads):
    hash_dict = defaultdict(list)
    res = {}
    thread_dic = {0: None, 1: 1, 2: 2, 3: 4, 4: 8}

    files = os.listdir(path)
    photo = PhotoHash(method, progress, start_time, dir_open(path))
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=thread_dic[threads]
    ) as executor:
        results = executor.map(photo.hash, files)

    for result in results:
        hash, file = result
        if hash is None:
            continue
        hash_dict[hash].append(file)

    for key in hash_dict:
        if len(hash_dict[key]) > 1:
            res[key] = hash_dict[key]
    return res


def find_simular_images(arg, signals):
    path = arg[0]
    os.chdir(path)
    progress = signals.progress
    start_time = time.time()
    hash_dict = get_hash_dict(path, progress, start_time, arg[1], arg[2])

    if hash_dict:
        newdir = os.path.join(path, "copies")
        if not os.path.isdir(newdir):
            os.mkdir(newdir)

    progress.emit(100, "Finishing up...")
    j = 0
    for paths in hash_dict.values():
        res = 0
        max_num = 0
        for i, name in enumerate(paths):
            image = Image.open(name)
            tmp = image.width * image.height
            if tmp > res:
                res = tmp
                max_num = i
            image.close()

        paths[-1], paths[max_num] = paths[max_num], paths[-1]

        for i, file in enumerate(paths):
            new_name = f"copy {j} {file}"
            new_path = os.path.join(newdir, new_name)
            if not os.path.isdir(new_path):
                os.rename(os.path.join(path, file), new_path)
                j += 1
                paths[i] = new_name
    res = (
        int(100 * (time.time() - start_time)) / 100,
        j,
        dir_open(path),
        path,
        hash_dict,
    )
    gc.collect()
    return res
