import re
import os
from PIL import Image
from PyQt5.QtCore import QThread

class Writer:
    def __init__(self):
        self.queue = []
        self.requests = []

    def save(self, img, path):
        Image.fromarray(img).save(path)

    def frame_to_string(self, frame, zeros=5):
        framestr = str(frame)
        framelen = len(framestr)
        return ("0"*zeros)[:-framelen]+framestr

    def save_frame_thread(self, *args):
        def run(worker):
            self.save_frame()

    def save_frame(self, image, path, frame=None):

        path = os.path.abspath(path)
        
        if len(os.path.splitext(path)[-1]) == 0:
            dirname = path
            name = (os.path.split(path)[-1], ".png")
            nframes = 5
        else:
            dirname, name = os.path.split(path)
            nframes = re.search("\[#*\]", name)
            if nframes is None:
                name = os.path.splitext(name)
                nframes = 5
            else:
                name = (name[:nframes.span()[0]], name[nframes.span()[1]:])
                nframes = len(nframes.group())-2

        try:
            os.makedirs(dirname, exist_ok=True)
        except Exception as err:
            print("Error saving file: {}".format(err))
        name = list(name)
        name[0] += "_"

        if frame is None:
            files = os.listdir(dirname)
            maxframe = -1
            for f in files:
                if f.startswith(name[0]):
                    if f.endswith(name[1]):
                        n = f[len(name[0]):-len(name[1])]
                        if n.isdecimal():
                            if len(n) == nframes:
                                maxframe = max(maxframe, int(n))
            frame = maxframe+1

        name = name[0]+self.frame_to_string(frame, nframes)+name[1]
        outname = os.path.join(dirname, name)
        try:
            self.save(image, outname)
            print("Saved {}".format(outname))
        except Exception as err:
            print("Error saving file: {}".format(err))

    def sync(self):
        self.queue += self.requests
        self.requests = []
    
    def request(self, *args):
        self.requests.append(args)

    def update(self):
        while len(self.queue) > 0:
            self.save_frame(*self.queue.pop(0))
