from rdapp.program import Program, Texture, FBO, DFBO
from rdapp import utils
import copy
import numpy as np
from PIL import Image
import os

class Renderer:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.queue = []

        self.blitter = app.blitter

        self.job = None
        self.color_program = None
        self.depth_program = None
        
        self.depth_fbo = None
        self.color_fbo = None
        self.color_image = None
        self.depth_image = None


        self.preview_fbo = None
        self.finished = True
        self.cancel = False

    def add_queue(self, job):
        self.queue.append(job)

    def set_job(self, job):
        # print("SETTING JOB")
        self.job = job

        self.depth_program = Program(
            self.ctx, *self.app.builder.depth(job.project, job.config))
        self.depth_program.set_uniforms({
            "render_size": job.depth_size,
            "tex": 1,
            "depth_texture": 0
        })

        self.color_program = Program(
            self.ctx, *self.app.builder.color(job.project, job.config))
        self.color_program.set_uniforms({
            "render_size": job.depth_size,
            "tex": 1,
            "depth_texture": 0
        })

        self.preview_fbo = FBO(self.ctx, job.preview_size, 4)
        self.preview_fbo.fbo.clear(0, 0, 0, 0)

    def clear_job(self):
        # print("CLEARING JOB")
        self.job = None
        if self.depth_program: self.depth_program.release()
        self.depth_program = None
        if self.color_program: self.color_program.release()
        self.color_program = None
        if self.preview_fbo: self.preview_fbo.release()
        self.preview_fbo = None

    def set_frame(self, frame):
        self.color_image = np.zeros(
            (self.job.color_size[1], self.job.color_size[0], 4), np.uint8)
        if self.job.config.depth:
            self.depth_image = np.zeros(
                (self.job.color_size[1]*self.job.aa, self.job.color_size[0]*self.job.aa), np.uint16)

        self.app.frame = frame
        self.app._update(1 / self.app.fps)
        self.app.reader.update(self.app.time)
        self.depth_program.set_uniforms(self.job.project.get_uniforms())
        self.color_program.set_uniforms(self.job.project.get_uniforms())

    def clear_frame(self):
        self.color_image = None
        self.depth_image = None


    def set_patch(self, patch):
        # print("New patch: {} of {}, Size: {} ".format(
        #     self.job.current_patch+1, len(self.job.patches), patch.size))

        if self.depth_fbo:
            self.depth_fbo.resize((patch.width * self.job.aa,
                                   patch.height * self.job.aa))
        else:
            self.depth_fbo = DFBO(
                self.ctx, (patch.width * self.job.aa, patch.height * self.job.aa), 4)
        self.depth_fbo.fbo.clear(0, 0, 0, 0)

        if self.color_fbo:
            self.color_fbo.resize((patch.width * self.job.aa, patch.height * self.job.aa))
        else:
            self.color_fbo = FBO(
                self.ctx, (patch.width * self.job.aa, patch.height * self.job.aa), 4)
        self.color_fbo.fbo.clear(0, 0, 0, 0)

        self.depth_program.set_uniforms({
            "patch_size": (patch.width*self.job.aa, patch.height*self.job.aa),
            "patch_pos": (patch.x*self.job.aa, patch.y*self.job.aa),
            "use_depth_tex": False,
        })

        self.color_program.set_uniforms({
            "patch_size": (patch.width*self.job.aa, patch.height*self.job.aa),
            "patch_pos": (patch.x*self.job.aa, patch.y*self.job.aa),
        })

    def continue_patch(self):
        self.depth_program.set_uniforms({
            "use_depth_tex": True,
        })

    def submit_frame(self):
        print("Frame {} finished".format(self.job.frame))
        # print("Last frame?", self.job.last_frame, self.job.frame, len(self.job.frames))
        if self.job.snap:
            path = self.app.writer.save_frame(self.color_image, self.job.config.snap_path, None)
            if self.job.config.depth:
                path = os.path.splitext(path)[0] + "_depth.png"
                self.app.writer.save(self.depth_image, path)
        else:
            path = self.job.config.path
            self.app.writer.save_frame(self.color_image, path, self.job.frame)
            if self.job.config.depth:
                path = path + "_depth"
                self.app.writer.save_frame(self.depth_image, path, self.job.frame)



    def submit_job(self):
        # print("Job {} finished".format(self.job.path))
        if self.job.config.mp4:
            self.save_mp4(self.job)

    def save_mp4(self, job):
            print("Saving mp4...")
            import os
            audio = self.app.audio.segment
            if audio:
                time1 = job.frames[0]/job.fps*1000
                time2 = job.frames[job.current_frame]/job.fps*1000
                time_len = int(time2-time1)
                time1 = max(0, min(len(audio)-1, int(time1)))
                time2 = max(0, min(len(audio)-1, int(time2)))
                audio_len = int(time2-time1)

                if audio_len < 10:
                    audio = None
                else:
                    audio = audio[time1:time2]
                    if len(audio) < time_len:
                        from pydub import AudioSegment
                        audio += AudioSegment.silent(duration=time_len-len(audio))

            path = os.path.join(job.path,  os.path.split(job.path)[-1]+"_%05d.png")
            self.app.writer.save_mp4(path, job.fps, job.frames[0], job.frames[job.current_frame], audio)

    def submit_queue(self):
        self.finished = True
        print("Render Finished")
        pass

    def next_job(self):
        while len(self.queue) > 0:
            job = self.queue.pop(0)
            if len(job.frames) != 0 and len(job.patches) != 0:
                self.set_job(job)
                return True
        return False

    def advance(self):
        if self.cancel:
            self.cancel = False
            self.clear_frame()
            self.submit_job()
            self.clear_job()


        if not self.job:
            if not self.next_job():
                self.submit_queue()
                return
        if self.job.first_patch:
            if self.job.first_march:
                self.set_frame(self.job.frame)
        if self.job.first_march:
            self.set_patch(self.job.patch)
        else:
            self.continue_patch()
        self.render_depth_patch()
        if not self.job.last_march:
            self.render_preview(self.depth_fbo.tex)
        else:
            self.render_color_patch()
            self.write_color_patch()
            if self.job.config.depth:
                self.write_depth_patch()
            self.render_preview(self.color_fbo.tex)
            if self.job.last_patch:
                self.submit_frame()
                self.clear_frame()
                if self.job.last_frame:
                    # print("JOB CLEARING")
                    self.submit_job()
                    self.clear_job()
                    if not self.next_job():
                        self.submit_queue()
        if self.job:
            self.job.advance()

    def render_depth_patch(self):
        self.app.texture.tex.use(1)
        self.depth_fbo.tex.use()
        self.depth_program.render(self.depth_fbo.fbo)
        self.depth_fbo.swap()

    def render_color_patch(self):
        self.app.texture.tex.use(1)
        self.depth_fbo.tex.use()
        self.color_program.render(self.color_fbo.fbo)

    def write_color_patch(self):
        data = np.frombuffer(self.color_fbo.tex.read(), np.uint8)
        data = data.reshape(self.job.patch.height * self.job.aa, self.job.patch.width * self.job.aa, 4)
        if self.job.aa > 1:
            data = np.uint8(Image.fromarray(data).resize((self.job.patch.width, self.job.patch.height), Image.BILINEAR))
        self.color_image[self.job.patch.y:self.job.patch.y+self.job.patch.height,
                   self.job.patch.x:self.job.patch.x+self.job.patch.width] = data

    def write_depth_patch(self):
        data = np.frombuffer(self.depth_fbo.tex.read(), np.uint8).astype("float32")/255
        data = data.reshape(self.job.patch.height * self.job.aa, self.job.patch.width * self.job.aa, 4)
        fix = 256.0/255.0
        data = data[...,0]*fix/1.0+data[...,1]*fix/255.0

        data = 1.0-data

        if self.job.config.depth_mask:
            color = np.frombuffer(self.color_fbo.tex.read(), np.uint8).astype("float32")/255.0
            color = color.reshape(self.job.patch.height * self.job.aa, self.job.patch.width * self.job.aa, 4)
            data = data * color[...,-1]
            
        data = np.uint16(data * np.iinfo(np.uint16).max)
        self.depth_image[self.job.patch.y*self.job.aa:self.job.patch.y*self.job.aa+self.job.patch.height*self.job.aa,
                   self.job.patch.x*self.job.aa:self.job.patch.x*self.job.aa+self.job.patch.width*self.job.aa] = data

    def render_preview(self, tex):
        rx, ry = (a/b for a, b in zip(self.job.preview_size, self.job.color_size))
        viewport = (self.job.patch.x * rx, self.job.patch.y * ry,
                    self.job.patch.width * rx, self.job.patch.height * ry)
        self.preview_fbo.fbo.clear(0, 0, 0, 1, viewport=viewport)
        self.blitter.render(self.preview_fbo.fbo, tex, viewport)
        self.app.screen.clear(0, 0, 0, 0)
        self.blitter.render(self.app.screen, self.preview_fbo.tex, self.app.live_config.viewport)

import os

class RenderJob:
    def __init__(self, project, config, frames=None, snap=False):
        self.project = project
        self.fps = self.project.fps
        self.snap = snap
        self.config = config
        self.path = config.path
        if not self.snap:
            name = os.path.split(self.path)[-1]
            folders = os.listdir(self.path)
            max_ = -1
            for f in folders:
                if f.startswith(name):
                    if len(f[len(name):]) == 5:
                        if f[len(name):].isdecimal():
                            max_ = max(max_, int(f[len(name):]))
            max_ += 1
            self.path = os.path.join(self.path, name+self.project.app.writer.frame_to_string(max_))

        # self.save_depth = config.save_depth
        if frames:
            self.frames = frames
        else:
            self.frames = range(config.frames[0], config.frames[1]+1)
        self.color_size = config.size
        self.aa = config.aa
        self.depth_size = self.color_size[0] * \
            self.aa, self.color_size[1] * self.aa
        self.max_patch = config.max_patch
        self.patches = self.find_patches(self.color_size, self.max_patch, self.aa)
        self.marches = int(np.ceil(config.steps / config.steps_max))
        self.current_patch = 0
        self.current_march = 0
        self.current_frame = 0

        self.preview_size = self.color_size
        # if self.preview_size[0] > config.preview_max_size or self.preview_size[0] > config.preview_max_size:
        #     self.preview_size = utils.fit(
        #         self.color_size, (config.preview_max_size,)*2)
        #     self.preview_size = tuple(int(x) for x in self.preview_size)

        self.done = False

    def advance(self):
        if not self.done:
            if self.last_march:
                self.current_march = 0
                if self.last_patch:
                    self.current_patch = 0
                    if self.last_frame:
                        self.done = True
                    else:
                        self.current_frame += 1
                else:
                    self.current_patch += 1
            else:
                self.current_march += 1

    @property
    def patch(self):
        return self.patches[self.current_patch]

    @property
    def frame(self):
        return self.frames[self.current_frame]

    @property
    def last_march(self):
        return self.current_march >= self.marches-1

    @property
    def first_march(self):
        return self.current_march == 0

    @property
    def first_patch(self):
        return self.current_patch == 0

    @property
    def last_patch(self):
        return self.current_patch == len(self.patches) - 1

    @property
    def first_frame(self):
        return self.current_frame == 0

    @property
    def last_frame(self):
        return self.current_frame == len(self.frames) - 1

    @property
    def progress(self):
        if self.is_done:
            return 1
        else:
            return ((self.current_patch * self.marches + self.current_march) /
                    (len(self.patches) * self.marches))

    def find_patches(self, size, max_patch, aa):
        patches = []
        patches_x = int(np.ceil(size[0]/(max_patch//aa)))
        patches_y = int(np.ceil(size[1]/(max_patch//aa)))
        # print(patches_y)
        patch_width = int(np.ceil(size[0] / patches_x))
        patch_height = int(np.ceil(size[1] / patches_y))
        for x in range(patches_x):
            for y in range(patches_y):
                pw = patch_width
                ph = patch_height
                if x == patches_x - 1:
                    if size[0] % pw != 0:
                        pw = size[0] % pw
                if y == patches_y - 1:
                    if size[1] % ph != 0:
                        ph = size[1] % ph
                patches.append(Patch(x*patch_width, y*patch_height, pw, ph))
        return patches

    def infer_frames(self, txt):
        frames = []
        tokens = txt.split(",")
        for t in tokens:
            t = t.replace(" ", "")
            t = t.split("-")
            if len(t) == 1:
                try:
                    frames.append(int(t[0]))
                except:
                    pass
            elif len(t) > 1:
                try:
                    frames += list(range(int(t[0]), int(t[1])+1))
                except:
                    pass
        return frames


class Patch:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height

    @property
    def size(self):
        return self.width, self.height
