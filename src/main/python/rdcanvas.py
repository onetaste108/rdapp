from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal as Signal

from glcanvas import Canvas
from mouse import Mouse
import time

class RDCanvas(Canvas):
    message = Signal(str)
    def __init__(self, item, app, controller):
        super().__init__(item)
        self.app = app
        self.app_state = None
        self.controller = controller
        self.mouse = Mouse()
        self.ptime = 0
        self.time = 0
        self.dtime = 0
        self._time = time.time()
        self.width, self.height = 64, 64
        self.set_fps(1000)

    def init(self):
        self.app.init()
        # self.app.load_texture("img/SRC_00003.jpg")
        
    def sync(self):
        self.ptime = self.time
        self.time = time.time() - self._time
        self.dtime = self.time - self.ptime
        # print("Target FPS", self.fps)
        # print("Actual FPS", 1 / self.dtime)
        
        # if self.fps != self.app.fps:
        #     self.set_fps(self.app.fps)

        log = self.controller.log.read()
        if len(log) > 0:
            self.controller.logChanged.emit(log)

        if self.app.states["project_loaded"]:
            self.app.states["project_loaded"] = False
            self.send_message("project_loaded")

        if self.app._state != self.app_state:
            self.app_state = self.app._state
            self.controller.state = self.app_state

        if self.controller.timeline.fps != self.app.fps:
            self.controller.timeline.set_fps(self.app.fps)

        self.app.resize(self.GLCanvas.width(), self.GLCanvas.height())
        self.GLCanvas.setProperty("renderViewport", QtCore.QRectF(*self.app.live_config.viewport))

        self.app.sync(self.dtime)

        self.controller.timeline.time = self.app.time
        self.controller.propModel.update()


    def resize(self, width, height):
        self.width, self.height = width, height
        self.app.resize(self.GLCanvas.width(), self.GLCanvas.height())
        self.app.sync(self.dtime)

    def render(self):
        self.app.draw()
        pass

    def mouse_moved(self, e):
        self.mouse.moved(e.x(), e.y())

        if e.modifiers() == QtCore.Qt.AltModifier:
            scale = 0.005
            self.app.project.camera.translate(0, 0, -(self.mouse.dy*scale + self.mouse.dx*-scale))
        elif e.modifiers() == QtCore.Qt.ControlModifier:
            scale = 0.01
            self.app.project.camera.translate(self.mouse.dx*-scale, self.mouse.dy*-scale)
        elif e.modifiers() == QtCore.Qt.ShiftModifier:
            scale = 0.005
            if e.buttons() & QtCore.Qt.RightButton:
                self.app.project.camera.rotate(0, 0, self.mouse.dy*scale + self.mouse.dx*-scale)
            else:
                self.app.project.camera.rotate(self.mouse.dy*scale, self.mouse.dx*-scale)
        else:
            scale = 0.01
            self.app.project.camera.rotate_from(self.mouse.dy*scale, self.mouse.dx*-scale)

    def mouse_pressed(self, e):
        self.controller.unfocus.emit()
        self.mouse.pressed(e.x(), e.y())

    def send_message(self, message):
        self.message.emit(message)