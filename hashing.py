import os
import time

from PIL import Image, ImageFile
from send2trash import send2trash

from multi_worker import MultyWorker

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


def dir_open(source_dir, signals=None):
    os.chdir(source_dir)
    cnt = 0
    for _, _, files in os.walk(source_dir):
        for file in files:
            file = file.lower()
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                cnt += 1
    return cnt


def uncopy(source_dir, signals):
    def exit_function():
        try:
            if len(os.listdir(new_dir)) == 0:
                os.rmdir(new_dir)
            old_pwd = os.getcwd()
            os.chdir(source_dir)
            send2trash("DONT DELETE.txt")
            os.chdir(old_pwd)
        except Exception:
            pass
        return dir_open(source_dir)

    new_dir = os.path.join(source_dir, "copies")
    if not os.path.isdir(new_dir):
        return exit_function()

    initial_names = {}
    if os.path.isfile(os.path.join(source_dir, "DONT DELETE.txt")):
        with open(
            os.path.join(source_dir, "DONT DELETE.txt"), "r", encoding="utf-8"
        ) as file:
            for string in file:
                string = string.split(" -- ")
                initial_names[string[0]] = " -- ".join(string[1:]).strip()
    else:
        return exit_function()

    for name in os.listdir(new_dir):
        try:
            os.rename(
                os.path.join(new_dir, name),
                initial_names[name],
            )
        except OSError:
            continue

    return exit_function()


def delete(arg, signals):
    source_dir = arg[0]
    hash_dict = arg[1]
    uncopy(source_dir, signals)

    old_pwd = os.getcwd()
    for value in hash_dict.values():
        head = os.path.dirname(value[0])
        os.chdir(head)
        for i in range(len(value) - 1):
            send2trash(os.path.basename(value[i]))
    os.chdir(old_pwd)
    return dir_open(source_dir)


def get_hash_dict(source_dir, progress, start_time, method, threads):
    thread_dic = {0: 3 * os.cpu_count() // 4, 1: 1, 2: 2, 3: 4, 4: 8}

    worker = MultyWorker(method, thread_dic[threads], source_dir)
    res = worker.work(progress, start_time)

    return res


def find_simular_images(arg, signals):
    source_dir = arg[0]
    progress = signals.progress
    start_time = time.time()
    hash_dict = get_hash_dict(source_dir, progress, start_time, arg[1], arg[2])

    if hash_dict:
        new_dir = os.path.join(source_dir, "copies")
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

    progress.emit(100, "Finishing up...")
    j = 0
    copies_list = []
    for paths in hash_dict.values():
        res = 0
        max_num = 0
        for i, path in enumerate(paths):
            image = Image.open(path)
            tmp = image.width * image.height
            if tmp > res:
                res = tmp
                max_num = i
            image.close()

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
            os.path.join(source_dir, "DONT DELETE.txt"), "w", encoding="utf-8"
        ) as file:
            file.writelines(copies_list)

    res = (
        int(100 * (time.time() - start_time)) / 100,
        j,
        dir_open(source_dir),
        source_dir,
        hash_dict,
    )
    return res
