from rdapp.program import Program


class Blitter:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = Program(self.ctx, *self.app.builder.blit())

    def render(self, target, texture, viewport=None):
        self.program.set_uniforms({
            "render_size": (1, 1),
            "patch_size": (1, 1),
            "patch_pos": (0, 0)
        })
        if viewport:
            _viewport = target.viewport
            target.viewport = viewport
        texture.use()
        self.program.render(target)
        if viewport:
            target.viewport = _viewport
