import numpy as np
import moderngl


class Program:
    def __init__(self, ctx, vert, frag):
        self.ctx = ctx
        self.quad = self.ctx.buffer(np.float32(
            [-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]))
        self.prog = self.ctx.program(
            vertex_shader=vert,
            fragment_shader=frag
        )
        self.vao = self.ctx.vertex_array(self.prog, self.quad, "a_pos")

    def render(self, target=None):
        if target:
            target.use()
        self.vao.render()

    def set_uniforms(self, uniforms):
        for u in uniforms:
            try:
                self.prog[u] = uniforms[u]
            except Exception as err:
                pass
                # print(err)

    def release(self):
        self.vao.release()
        self.prog.release()
        self.quad.release()


class FBO:
    def __init__(self, ctx, size, depth=4):
        self.ctx = ctx
        self.build(size, depth)

    def build(self, size, depth):
        self.size = size
        self.depth = depth
        self.tex = self.ctx.texture(size, depth)
        self.fbo = self.ctx.framebuffer([self.tex])

    def release(self):
        if self.tex:
            self.tex.release()
        if self.fbo:
            self.fbo.release()

    def resize(self, size):
        if self.size != size:
            self.release()
            self.build(size, self.depth)


class DFBO:
    def __init__(self, ctx, size, depth=4):
        self.ctx = ctx
        self.build(size, depth)

    def build(self, size, depth):
        self.size = size
        self.depth = depth
        self.fbo1 = FBO(self.ctx, size, depth)
        self.fbo2 = FBO(self.ctx, size, depth)

    def swap(self):
        tmp = self.fbo1
        self.fbo1 = self.fbo2
        self.fbo2 = tmp

    def release(self):
        self.fbo1.release()
        self.fbo2.release()

    def resize(self, size):
        if self.size != size:
            self.release()
            self.build(size, self.depth)

    @property
    def fbo(self):
        return self.fbo1.fbo

    @property
    def tex(self):
        return self.fbo2.tex


class Texture:
    def __init__(self, ctx):
        self.ctx = ctx
        self.tex = self.ctx.texture((64, 64), 4)

    def set(self, img):
        img_size = img.shape[:2][::-1]
        if len(img.shape) == 2:
            img_depth = 1
        else:
            img_depth = img.shape[2]
        if self.tex.size != img_size or self.tex.depth != self.tex.depth:
            self.tex.release()
            self.tex = self.ctx.texture(img_size, img_depth, img)
        else:
            self.tex.write(img)

    def use(self, n=0):
        self.tex.use(n)

    def release(self):
        self.tex.release()
        self.tex = None
