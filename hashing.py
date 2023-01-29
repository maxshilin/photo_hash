import os
import time
import imghdr
from PIL import Image, ImageFile
from send2trash import send2trash
from multi_worker import MultyWorker

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760


def dir_open(path, signals=None):
    os.chdir(path)
    cnt = 0
    for _, _, files in os.walk(path):
        for file in files:
            file = file.lower()
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                cnt += 1
    return cnt


def uncopy(path, signals):
    def exit_function():
        try:
            if len(os.listdir(new_dir)) == 0:
                os.rmdir(new_dir)
            os.remove(os.path.join(path, "tmp.txt"))
        except OSError:
            pass
        return dir_open(path)

    new_dir = os.path.join(path, "copies")
    if not os.path.isdir(new_dir):
        return exit_function()

    initial_names = None
    if os.path.isfile(os.path.join(path, "tmp.txt")):
        with open(
            os.path.join(path, "tmp.txt"), "r", encoding="utf-8"
        ) as file:
            initial_names = [name.strip() for name in file.readlines()]
    else:
        return exit_function()

    for name in os.listdir(new_dir):
        try:
            os.rename(
                os.path.join(new_dir, name),
                initial_names[int(name.split(".")[0][5:])],
            )
        except OSError:
            continue

    return exit_function()


def delete(arg, signals):
    path = arg[0]
    hash_dict = arg[1]
    new_dir = os.path.join(path, "copies")

    old_pwd = os.getcwd()
    os.chdir(new_dir)
    if os.path.isdir(new_dir):
        if not hash_dict:
            return uncopy(path, signals)
        for value in hash_dict.values():
            for i in range(len(value) - 1):
                send2trash(value[i])
    os.chdir(old_pwd)
    return uncopy(path, signals)


def get_hash_dict(path, progress, start_time, method, threads):
    thread_dic = {0: 3 * os.cpu_count() // 4, 1: 1, 2: 2, 3: 4, 4: 8}

    worker = MultyWorker(method, thread_dic[threads], path)
    res = worker.work(progress, start_time)

    return res


def find_simular_images(arg, signals):
    path = arg[0]
    progress = signals.progress
    start_time = time.time()
    hash_dict = get_hash_dict(path, progress, start_time, arg[1], arg[2])

    if hash_dict:
        new_dir = os.path.join(path, "copies")
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

    progress.emit(100, "Finishing up...")
    j = 0
    copies_list = []
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
            new_name = f"copy {j}.{imghdr.what(file)}"
            new_path = os.path.join(new_dir, new_name)
            if not os.path.isdir(new_path):
                os.rename(file, new_path)
                j += 1
                paths[i] = new_name
                copies_list.append(file + "\n")

    with open(os.path.join(path, "tmp.txt"), "w", encoding="utf-8") as file:
        file.writelines(copies_list)

    res = (
        int(100 * (time.time() - start_time)) / 100,
        j,
        dir_open(path),
        path,
        hash_dict,
    )
    return res
