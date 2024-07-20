import os
from jutility import util

music_dir = "/run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_R9ARC000HJF/SD card/Music"

printer = util.Printer("albums", ".")
albums = []
with util.Timer("List albums"):
   for d in sorted(os.listdir(music_dir)):
       if os.path.isdir(os.path.join(music_dir, d)):
           for a in sorted(os.listdir(os.path.join(music_dir, d))):
               if os.path.isdir(os.path.join(music_dir, d, a)):
                   printer(a, flush=True)
                   albums.append(a)
