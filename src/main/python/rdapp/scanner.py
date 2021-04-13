import numpy as np
from rdapp.program import Program, FBO
import threading
import mcubes
import os

class Scanner:
    def __init__(self, app):
        self.app = app
        self.scan_program = None
        self.finished = True
        self.cancel = False
        self.build_requested = False

        self.data = None
        self.fbo = None

    def start(self):
        print("Scanning...")
        self.box = self.app.render_config.scan_box
        self.res = self.app.render_config.scan_res
        self.z = 0
        self.data = np.empty([self.res]*3, np.uint8)

        self.scan_program = Program(
            self.app.ctx, *self.app.builder.scan(self.app.project, self.app.render_config))
        self.scan_program.set_uniforms({
            "render_size": [self.res, self.res],
            "patch_size": [self.res, self.res],
            "patch_pos": [0,0],
            "_SCAN_BOX": self.box
        })
        self.scan_program.set_uniforms(self.app.project.get_uniforms())
        self.fbo = FBO(self.app.ctx, [self.res, self.res])

        self.path = self.app.render_config.path
        name = os.path.split(self.path)[-1]
        folders = os.listdir(self.path)
        max_ = -1
        for f in folders:
            if f.startswith(name):
                if f.endswith(".obj"):
                    if len(f[len(name):-4]) == 5:
                        if f[len(name):-4].isdecimal():
                            max_ = max(max_, int(f[len(name):-4]))
        max_ += 1
        self.path = os.path.join(self.path, name+self.app.writer.frame_to_string(max_)+".obj")


    def clear(self):
        if self.fbo: self.fbo.release()
        self.fbo = None
        if self.scan_program: self.scan_program.release()
        self.scan_program = None

    def clear_data(self):
        self.data = None

    def make_obj(self, data, path):
        def fn(data):
            data = np.float64(data)/255
            vertices, triangles = mcubes.marching_cubes(data, 0.5)
            mcubes.export_obj(vertices, triangles, path)
            print("Object saved: {}".format(path))
        thread = threading.Thread(target=fn, args=(data,))
        thread.run()

    def advance(self):
        if self.cancel:
            self.clear()
            self.clear_data()
            self.finished = True

        if not self.finished:
            self.scan_program.set_uniforms({
                "_SCAN_Z": self.z/self.res + 0.5/self.res
            })
            self.scan_program.render(self.fbo.fbo)
            data = np.frombuffer(self.fbo.tex.read(), np.uint8)
            data = data.reshape(self.res, self.res, 4)
            self.data[self.z] = data[...,0]
            self.z += 1

            self.app.screen.clear(0, 0, 0, 0)
            self.app.blitter.render(self.app.screen, self.fbo.tex, self.app.live_config.viewport)

            if self.z == self.res-1:
                print("Building object...")

            if self.z == self.res:
                self.clear()
                self.finished = True
                self.make_obj(self.data, self.path)
                self.clear_data()
