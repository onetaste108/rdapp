from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property
from PyQt5 import QtQml
from PyQt5.QtGui import QCursor

import utils
import math
import os

class Controller(QtCore.QObject):
    def __init__(self, appctx, app, timeline, propModel, configModels, style, log):
        super().__init__()
        self.log = log
        self.appctx = appctx
        self.app = app
        self.timeline = timeline
        self.propModel = propModel
        self._timelinePropertyName = ""
        self._tempPlayState = False
        self.cursor = (0,0)
        self._state = "LIVE"
        self.style = style
        self.configModels = configModels
        self.appctx.app.load_project.connect(self.load)

    shutdown = Signal()

    @Slot(str)
    def load(self, path):
        self.app.load_project(path)

    @Slot(int)
    def set_cam(self, n):
        if n == 0:
            self.app.cam.reset()
        if n == 1:
            self.app.cam.reset()
            self.app.cam.translate(0, 0, -3)
        if n == 2:
            self.app.cam.reset()
            self.app.cam.rotate(0, -math.pi/2, 0)
            self.app.cam.translate(0, 0, -3)
        if n == 3:
            self.app.cam.reset()
            self.app.cam.rotate(0, -math.pi*2/2, 0)
            self.app.cam.translate(0, 0, -3)
        if n == 4:
            self.app.cam.reset()
            self.app.cam.rotate(0, -math.pi*3/2, 0)
            self.app.cam.translate(0, 0, -3)
        if n == 5:
            self.app.cam.reset()
            self.app.cam.rotate(-math.pi/2, 0, 0)
            self.app.cam.translate(0, 0, -3)
        if n == 6:
            self.app.cam.reset()
            self.app.cam.rotate(math.pi/2, 0, 0)
            self.app.cam.translate(0, 0, -3)

    @Slot(result=str)
    def version(self):
        return "v{}.{}.{}".format(*self.app.version)

    @Slot()
    def default(self):
        self.app.default_project()

    @Slot(result = str)
    def project_path(self):
        if self.app.project_path is not None:
            print("APP", self.app.project_path)
            return self.app.project_path
        else:
            return ""

    @Slot(str)
    def save_as(self, path):
        self.app.save_as(path)

    @Slot(QtCore.QVariant)
    def drop(self, urls):
        url = urls[0].toLocalFile()
        if os.path.splitext(url)[-1].lower() == ".rd":
            self.load(url)
        else:
            self.app.set_file(url)

    @Slot()
    def render(self):
        self.app.render()

    @Slot()
    def snap(self):
        self.app.snap()

    @Slot()
    def stop_render(self):
        self.app.stop_render()

    stateChanged = Signal(str)

    @Property(str, notify=stateChanged)
    def state(self):
        return self._state

    @state.setter
    def state(self, t):
        self._state = t
        self.stateChanged.emit(t)

    timeChanged = Signal(float)

    @Property(float)
    def time(self):
        return self.app.project.time

    @time.setter
    def time(self, t):
        self.app.project.time = t
        self.timeChanged.emit(t)

    @Slot(str)
    def setTimeline(self, name):
        self._timelinePropertyName = name
        self.timeline.set_value(self.app.project.values[name])
        self.timelinePropertyNameChanged.emit(self._timelinePropertyName)

    timelinePropertyNameChanged = Signal(str)

    @Property(str, notify=timelinePropertyNameChanged)
    def timelinePropertyName(self):
        return self._timelinePropertyName

    @Slot(float)
    def setTime(self, time):
        self.app.project.time = time
        self.timeline.time = time

    @Slot()
    def tempPause(self):
        self._tempPlayState = self.app.playing
        self.app.stop()

    @Slot()
    def tempPlay(self):
        if self._tempPlayState:
            self.app.play()

    @Slot()
    def playPause(self):
        if self.app.playing:
            self.app.stop()
        else:
            self.app.play()

    @Slot(str)
    def runScript(self, code):
        code = code.replace("\u2029", "\n")
        # print(code)
        self.app.run_script(code)

    @Slot(result=str)
    def getProjectCode(self):
        return self.app.project.script

    @Slot(result=str)
    def getProjectShader(self):
        return self.app.project.code.code

    @Slot(str)
    def setProjectShader(self, code):
        code = code.replace("\u2029", "\n")
        self.app.set_shader(code)
        self.propModel.reset()

    def connect(self, rdcanvas):
        rdcanvas.message.connect(self.recieve_message)

    @Slot(QtCore.QObject)
    def qml_connect(self, item):
        from rdcanvas import RDCanvas
        rdcanvas = RDCanvas(item, self.app, self)
        rdcanvas.message.connect(self.recieve_message)

    codeUpdated = Signal()
    shaderUpdated = Signal()

    def recieve_message(self, *message):
        if message[0] == "project_loaded":
            self.codeUpdated.emit()
            self.shaderUpdated.emit()
            self.propModel.reset()
            self.style.set_theme(self.style.get_theme())
            for c in self.configModels:
                c.update()

    @Slot()
    def rememberCursor(self):
        self.cursor = QCursor.pos()

    @Slot()
    def resetCursor(self):
        QCursor.setPos(self.cursor)
    
    unfocus = Signal()
    logChanged = Signal(str)

class SettingsValue:
    def __init__(self, name, tp, ndim, set, get, _min=None, _max=None):
        self.name=name
        self.tp=tp
        self.ndim=ndim
        self._set=set
        self._get=get
        self._min = _min
        self._max = _max

    def get(self, i):
        if self.ndim > 1:
            if i < self.ndim:
                return str(self._get()[i])
            else: return ""
        else: return str(self._get())
        
    def set(self, value, i):
        val = None
        if self.tp == "float":
            val = utils.eval_float(value, self._min, self._max)
        if self.tp == "int":
            val = utils.eval_int(value, self._min, self._max)
        if self.tp in ("str", "file", "path") :
            val = utils.eval_str(value)
        if self.tp == "bool":
            val = utils.eval_bool(value)
        if val is not None:
            if self.ndim > 1:
                oldval = list(self._get())
                oldval[i] = val
                self._set(oldval)
            else:
                self._set(val)


class ConfigModel(QtCore.QAbstractListModel):
    resetSignal = Signal()

    def get_values(self):
        return []

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.values = dict(enumerate(self.get_values()))
        self.resetSignal.connect(self.reset)

    @Slot()
    def update(self):
        self.dataChanged.emit(self.index(0), self.index(len(self.values)-1))

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.values)

    def data(self, index, role):
        key = self.values[index.row()]
        if role == 0:
            return key.name
        if role == 1:
            return key.tp
        if role == 2:
            return key.ndim
        if role > 2 and role < 7:
            return key.get(role-3)

    def setData(self, index, value, role):
        key = self.values[index.row()]
        if role > 2 and role < 7:
            key.set(value, role-3)
        self.dataChanged.emit(index, index)
        return False

    def roleNames(self):
        return {
            0: b"name",
            1: b"tp",
            2: b"ndim",
            3: b"val1",
            4: b"val2",
            5: b"val3",
            6: b"val4"
        }

class ConfigModelGeneral(ConfigModel):
    def get_values(self):
            return (
                SettingsValue("Size", "int", 2, self.app.set_render_size, self.app.get_render_size, 1),
                SettingsValue("Snap Path", "path", 1, self.app.set_snap_path, self.app.get_snap_path),
                SettingsValue("Render Path", "path", 1, self.app.set_render_path, self.app.get_render_path),
                SettingsValue("Frames", "int", 2, self.app.set_render_frames, self.app.get_render_frames),
                SettingsValue("Depth", "bool", 1, self.app.set_render_depth, self.app.get_render_depth),
                SettingsValue("Save MP4", "bool", 1, self.app.set_render_mp4, self.app.get_render_mp4),
            )

class ConfigModelRender(ConfigModel):
    def get_values(self):
            return (
                SettingsValue("Antialiasing", "int", 1, self.app.set_render_aa, self.app.get_render_aa, 1),
                SettingsValue("Step Scale", "float", 1, self.app.set_render_step_scale, self.app.get_render_step_scale, 1),
                SettingsValue("Steps", "int", 1, self.app.set_render_steps, self.app.get_render_steps, 0),
                SettingsValue("Steps Max", "int", 1, self.app.set_render_steps_max, self.app.get_render_steps_max, 0),
                SettingsValue("Stop Dist", "float", 1, self.app.set_render_stop_dist, self.app.get_render_stop_dist, 0),
                SettingsValue("Patch Size", "int", 1, self.app.set_render_max_patch, self.app.get_render_max_patch, 1),
                SettingsValue("Max Depth", "float", 1, self.app.set_render_max_depth, self.app.get_render_max_depth),
                SettingsValue("Min Depth", "float", 1, self.app.set_render_min_depth, self.app.get_render_min_depth),
                SettingsValue("Depth Mask", "bool", 1, self.app.set_render_depth_mask, self.app.get_render_depth_mask),
                SettingsValue("Preview Size", "int", 1, self.app.set_render_preview_max_size, self.app.get_render_preview_max_size, 0),
            )

class ConfigModelPreview(ConfigModel):
    def __init__(self, app, style):
        self.style = style
        super().__init__(app)
    def get_values(self):
            return (
                SettingsValue("Downscale", "int", 1, self.app.set_live_downscale, self.app.get_live_downscale),
                SettingsValue("Step Scale", "float", 1, self.app.set_live_step_scale, self.app.get_live_step_scale),
                SettingsValue("Steps", "int", 1, self.app.set_live_steps, self.app.get_live_steps),
                SettingsValue("Stop Dist", "float", 1, self.app.set_live_stop_dist, self.app.get_live_stop_dist),
                SettingsValue("Max Depth", "float", 1, self.app.set_live_max_depth, self.app.get_live_max_depth),
                SettingsValue("Min Depth", "float", 1, self.app.set_live_min_depth, self.app.get_live_min_depth),
                SettingsValue("Margins", "float", 1, self.app.set_live_margins, self.app.get_live_margins),
                SettingsValue("Clear", "bool", 1, self.app.set_live_clear, self.app.get_live_clear),
                SettingsValue("Theme", "int", 1, self.style.set_theme, self.style.get_theme, 0, len(self.style.all_styles)-1),
            )

class ConfigModelProject(ConfigModel):
    def get_values(self):
            return (
                SettingsValue("FPS", "float", 1, lambda x: self.app.project.set_fps(x), lambda: self.app.fps, 0),
                SettingsValue("Audio", "file", 1, lambda x: self.app.set_audio(x), lambda: self.app.project.audio),
                SettingsValue("Video", "file", 1, lambda x: self.app.set_texture(x), lambda: self.app.project.texture),
                SettingsValue("Run Script", "bool", 1, lambda x: self.app.set_script_startup(x), self.app.get_script_startup)

            )

class Model(QtCore.QAbstractListModel):
    resetSignal = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.values = {}
        self.resetSignal.connect(self.reset)

    def appToModel(self):
        vals = [self.app.project.values[val] for val in self.app.project.values]
        modelvals = [SettingsValue(val._name, val.type, val.ndim, val.set_value, val.get_value) for val in vals]
        return modelvals

    def reset(self):
        self.beginResetModel()
        self.values = dict(enumerate(self.appToModel()))
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.values)

    def data(self, index, role):
        key = self.values[index.row()]
        if role == 0:
            return key.name
        if role == 1:
            return key.tp
        if role == 2:
            return key.ndim
        if role > 2 and role < 7:
            return key.get(role-3)

    def setData(self, index, value, role):
        key = self.values[index.row()]
        if role > 2 and role < 7:
            key.set(value, role-3)
        self.dataChanged.emit(index, index)
        return False

    def roleNames(self):
        return {
            0: b"name",
            1: b"tp",
            2: b"ndim",
            3: b"val1",
            4: b"val2",
            5: b"val3",
            6: b"val4"
        }



from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers.graphics import GLShaderLexer
from pygments.formatters import HtmlFormatter
from pygments.token import Token, Keyword


from styles import all_styles

class CodeEditorContext(QtCore.QObject):
    def __init__(self, styleContext):
        super().__init__()
        self.styleContext = styleContext
        self._s = 0

    @Slot(str, str, result=str)
    def formatCode(self, code, lang):
        style = self.styleContext._style
        fmt = ""
        if lang == "py":
            fmt = highlight(code, PythonLexer(), HtmlFormatter(
                nowrap=True, noclasses=True, cssclass="", nobackground=True, style=style))
        elif lang == "glsl":
            fmt = highlight(code, GLShaderLexer(), HtmlFormatter(
                nowrap=True, noclasses=True, cssclass="", nobackground=True, style=style))
        # elif lang == "pylog":
        #     fmt = highlight(code, PythonLexer(), HtmlFormatter(
        #         nowrap=True, noclasses=True, cssclass="", nobackground=True, style=style))
        return "<pre style='font-family:"+'jetbrains mono'+"'>"+fmt+"</pre>"


class StyleContext(QtCore.QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.all_styles = all_styles
        self.nstyles = len(self.all_styles)
        self.set_theme(self.app.app_config.theme)
        self._dark = True

    def set_theme(self, theme):
        self.set_style(self.all_styles[theme])
        self.app.app_config.theme = theme

    def get_theme(self):
        return self.app.app_config.theme

    def set_style(self, style):
        self._style = style

        color = self._style.background_color[1:]
        r = int(color[:2], 16)/255
        g = int(color[2:4], 16)/255
        b = int(color[4:], 16)/255
        self._dark = (r+g+b)/3 < 0.7

        self.backgroundChanged.emit(self.background)
        self.foregroundChanged.emit(self.foreground)
        self.accentChanged.emit(self.foreground)
        self.darkChanged.emit(self.dark)
        self.styleChanged.emit()

    styleChanged = Signal()
    backgroundChanged = Signal(str)
    foregroundChanged = Signal(str)
    accentChanged = Signal(str)
    darkChanged = Signal(bool)

    @Slot()
    def randomStyle(self):
        self.set_style(self.all_styles[random.randint(0, self.nstyles-1)])

    @Property(str, notify=backgroundChanged)
    def background(self):
        return self._style.background_color

    @Property(str, notify=foregroundChanged)
    def foreground(self):
        return "#"+self._style._styles[Token][0]

    @Property(str, notify=foregroundChanged)
    def accent(self):
        return "#"+self._style._styles[Keyword][0]

    @Property(bool, notify=foregroundChanged)
    def dark(self):
        return self._dark
