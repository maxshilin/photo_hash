import os
import time
from PIL import Image, ImageFile
from send2trash import send2trash
from multi_worker import MultyWorker

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


def dir_open(path, signals=None):
    os.chdir(path)
    return sum(
        os.path.isfile(f)
        for f in map(lambda x: x.name, os.scandir(path))
        if ".png" in f.lower() or ".jpg" in f.lower()
    )


def uncopy(path, signals):
    newdir = os.path.join(path, "copies")
    if os.path.isdir(newdir):
        with os.scandir(newdir) as it:
            for file in it:
                file = file.name
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
        for value in hash_dict.values():
            for i in range(len(value) - 1):
                send2trash(value[i])
    os.chdir(path)
    return uncopy(path, signals)


def get_hash_dict(path, progress, start_time, method, threads):
    thread_dic = {0: 3 * os.cpu_count() // 4, 1: 1, 2: 2, 3: 4, 4: 8}

    worker = MultyWorker(method, thread_dic[threads], path)
    res = worker.work(progress, start_time)

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
    return res
