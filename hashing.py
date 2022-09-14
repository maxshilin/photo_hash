from PIL import Image, ImageFile
import imagehash
from os import listdir, mkdir, rmdir
import os
import time
import worker
import concurrent.futures
from send2trash import send2trash
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 265949760

class photo_hash:
    def __init__(self, key, progress, start_time, Len):
        self.num = 0
        self.key = key
        self.progress = progress
        self.time = start_time
        self.Len = Len
        self.func_dic = {0: imagehash.phash, 1: imagehash.dhash,
                         2: imagehash.average_hash, 3: imagehash.whash,
                         4: imagehash.colorhash, 5: imagehash.crop_resistant_hash}

    def hash(self, path):
        self.num += 1
        self.progress.emit(100*self.num//self.Len, round(time.time() - self.time, 3))
        if worker.a is True:
            return None, None
        try:
            with Image.open(path) as im:
                hash = self.func_dic[self.key](im)
                im.close()
        except OSError:
            return None, None
        return str(hash), path


def dir_open(Path, signals=0):
    os.chdir(Path)
    return sum(os.path.isfile(f) for f in listdir(Path) if '.png' in f.lower() or '.jpg' in f.lower())


def uncopy(Path, signals):
    newdir = os.path.join(Path, 'copies')
    if os.path.isdir(newdir):
        for file in listdir(newdir):
            if 'copy ' in file:
                Str = file.replace('copy ', '')
                Str = Str[Str.find(' ') + 1:]
                try:
                    os.rename(os.path.join(newdir, file), os.path.join(Path, Str))
                except OSError:
                    continue
        if len(listdir(newdir)) == 0:
            rmdir(newdir)
    return dir_open(Path)


def delete(arg, signals):
    Path = arg[0]
    Dic = arg[1]
    newdir = os.path.join(Path, 'copies')
    os.chdir(newdir)
    if os.path.isdir(newdir):
        if not Dic:
            os.chdir(Path)
            return uncopy(Path, signals)
        for key in Dic.keys():
            for i in range(len(Dic[key]) - 1):
                send2trash(Dic[key][i])
    os.chdir(Path)
    return uncopy(Path, signals)


def hash_find(Path, progress, start_time, key, threads):
    dict = {}
    key_list = []
    thread_dic = {0: None, 1: 1, 2: 2, 3: 4, 4: 8}

    files = listdir(Path)
    photo = photo_hash(key, progress, start_time, dir_open(Path))
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_dic[threads]) as executor:
        results = executor.map(photo.hash, files)

    for result in results:
        hash, file = result
        if hash is None:
            continue
        if hash not in dict:
            dict[hash] = [file]
        else:
            dict[hash].append(file)
            key_list.append(hash)
    return dict, set(key_list)


def hash(arg, signals):
    Path = arg[0]
    os.chdir(Path)
    progress = signals.progress
    start_time = time.time()
    Dic, key_list = hash_find(Path, progress, start_time, arg[1], arg[2])

    List = {key: Dic[key] for key in key_list}
    Dic.clear()

    if key_list:
        newdir = os.path.join(Path, 'copies')
        if not os.path.isdir(newdir):
            mkdir(newdir)

    progress.emit(100, 'Finishing up...')
    j = 0
    for key in key_list:
        res = 0
        max_num = 0
        for i, name in enumerate(List[key]):
            im = Image.open(name)
            tmp = im.width * im.height
            if tmp > res:
                res = tmp
                max_num = i
            im.close()
        List[key][-1], List[key][max_num] = List[key][max_num], List[key][-1]

        for i, file in enumerate(List[key]):
            Str = f'copy {j} {file}'
            ppath = os.path.join(newdir, Str)
            if not os.path.isdir(ppath):
                os.rename(os.path.join(Path, file), ppath)
                List[key][i] = Str
                j += 1
    res = [int(100 * (time.time() - start_time)) / 100, j, dir_open(Path), Path, List]
    return res
