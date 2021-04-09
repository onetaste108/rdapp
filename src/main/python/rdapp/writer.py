import re
import os
from PIL import Image
from PyQt5.QtCore import QThread

import subprocess
import imageio_ffmpeg

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
        nframes = 5
        name = os.path.split(path)[-1] + "_", ".png"

        try:
            os.makedirs(path, exist_ok=True)
        except Exception as err:
            print("Error saving file: {}".format(err))
            return

        if frame is None:
            files = os.listdir(path)
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
        outname = os.path.join(path, name)
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

    def save_mp4(self, path, fps, start_frame, end_frame, sound):
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        save_path = os.path.split(path)[0]
        save_name = os.path.split(save_path)[1]
        save_path = os.path.split(save_path)[0]
        sound_path = os.path.join(save_path, "_sound.mp3")
        save_path = os.path.join(save_path, save_name+f"[{self.frame_to_string(start_frame)}-{self.frame_to_string(end_frame)}].mp4")

        import threading

        def fn():

            if sound is not None:
                sound.export(sound_path, format="mp3")

            process = subprocess.Popen([
                ffmpeg_exe] +
                ([] if sound is None else ["-i", sound_path])
                +
                [

                "-f", "image2",
                "-framerate", str(fps),
                "-start_number", str(start_frame),

                "-i", path,

                # "-frames:v", str(end_frame-start_frame),
                "-vf", "premultiply=inplace=1",
                "-r", str(fps),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "16",
                "-tune", "animation",
                "-shortest",
                save_path,
                "-y"
                ], stdout=subprocess.PIPE)
            print("Done")

        thread = threading.Thread(target=fn)
        thread.run()
        # fn()
