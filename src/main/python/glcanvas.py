from PyQt5 import QtGui, QtQuick, QtCore, QtQml
from PyQt5.QtCore import pyqtSignal as Signal, QObject

class GLRenderer(QtQuick.QQuickFramebufferObject.Renderer):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.initialized = False
        self.on_render = None
        self.resized = False

    def createFramebufferObject(self, size):
        self.resized = True
        return super().createFramebufferObject(size)

    def synchronize(self, GLCanvas):
        if not self.initialized:
            if GLCanvas.on_init:
                GLCanvas.on_init()
                self.initialized = True
        if self.resized:
            if GLCanvas.on_resize:
                GLCanvas.on_resize(self.framebufferObject().width(), self.framebufferObject().height())
                self.resized = False
        if not self.on_render:
            if GLCanvas.on_render:
                self.on_render = GLCanvas.on_render
        if GLCanvas.on_sync:
            GLCanvas.on_sync()

    def render(self):
        if self.on_render:
            self.on_render()
        self.window.resetOpenGLState()


class GLCanvas(QtQuick.QQuickFramebufferObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptedMouseButtons(QtCore.Qt.AllButtons)
        self.on_init = None
        self.on_sync = None
        self.on_render = None
        self.on_resize = None

    def createRenderer(self):
        return GLRenderer(self.window())


QtQml.qmlRegisterType(GLCanvas, "GL", 0, 1, "GLCanvas")


class Canvas(QtCore.QObject):
    fps_changed = Signal(float)
    def __init__(self, GLCanvas):
        super().__init__()
        self.GLCanvas = GLCanvas
        self.fps = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(GLCanvas.update)
        self.fps_changed.connect(self._set_fps)
        self._set_fps(60)

        GLCanvas.on_render = self.render
        GLCanvas.on_resize = self.resize
        GLCanvas.on_sync = self.sync
        GLCanvas.on_init = self.init
        GLCanvas.mouseMoveEvent = self.mouse_moved
        GLCanvas.mousePressEvent = self.mouse_pressed


    def set_fps(self, fps):
        self.fps_changed.emit(fps)

    def _set_fps(self, fps = 0):
        self.fps = fps
        if fps == 0:
            self.timer.stop()
        else:
            self.timer.setInterval(1000/fps)
            self.timer.start()


    def init(self):
        pass

    def sync(self):
        pass

    def render(self):
        pass

    def resize(self, width, height):
        pass

    def mouse_moved(self, e):
        pass

    def mouse_pressed(self, e):
        pass
