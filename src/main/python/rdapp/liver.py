from rdapp.program import Program, Texture, FBO, DFBO
from rdapp.blitter import Blitter
import numpy as np

class Liver:
    def __init__(self, app):
        self.app = app
        self.ctx = self.app.ctx
        self.builder = self.app.builder
        self.program = None
        self.fbo = FBO(self.ctx, [4,4])
        self.blitter = Blitter(self.app)

    def build(self):
        return Program(
            self.ctx, *self.builder.live(self.app.project, self.app.live_config))

    def sync(self):
        if self.app._live_build_requested:
            try:
                program = self.build()
                if self.program:
                    self.program.release()
                self.program = program
                self.app._live_build_requested = False
                if self.app._code_update_requested:
                    self.app._code_accepted()
            except Exception as err:
                print("Error building program: {}".format(err))
                if self.app._code_update_requested:
                    self.app._code_rejected()
                    try:
                        program = self.build()
                        if self.program:
                            self.program.release()
                        self.program = program
                        self.app._live_build_requested = False
                    except Exception as err:
                        print("Error building program: {}".format(err))
        if self.program:
            self.program.set_uniforms(self.app.live_config.get_uniforms())
            self.program.set_uniforms(self.app.project.get_uniforms())

    def render(self):
        if self.program:
            if self.app.live_config.clear:
                self.app.screen.clear(0, 0, 0, 0)
            size = self.app.screen.size
            size = size[0] // self.app.live_config.downscale, size[1] // self.app.live_config.downscale
            self.fbo.resize(size)
            self.fbo.fbo.clear()
            self.program.render(self.fbo.fbo)
            self.blitter.render(self.app.screen, self.fbo.tex)
