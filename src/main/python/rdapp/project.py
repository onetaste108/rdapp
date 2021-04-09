from rdapp.camera import Camera
from rdapp.track import Track
from rdapp import utils
import numpy as np
from PyQt5 import QtCore
import os

class Project:
    def __init__(self, app):
        self.app = app
        pass

    def save(self):
        out = {}
        out["play"] = self.play
        out["time"] = self.time
        out["fps"] = self.fps
        out["camera"] = list(self.camera.get())
        out["texture"] = self.texture
        out["audio"] = self.audio
        out["values"] = {}
        for val in self.values:
            out["values"][val] = self.values[val].save()
        out["code"] = self.code.code
        out["script"] = self.script
        return out

    @staticmethod
    def load(app, data):
        project = Project(app)
        project.play = data["play"]
        project.time = data["time"]
        project.fps = data["fps"]
        project.camera = Camera(data["camera"])
        project.texture = data["texture"]
        project.audio = data["audio"]
        project.values = {}
        for val in data["values"]:
            project.values[val] = Value.load(project, data["values"][val])
        project.code = CodeInfo(data["code"])
        project.script = data["script"]
        project.backup_code = None
        project.backup_values = None
        project.create_values()
        return project

    @staticmethod
    def default(app, resources):
        project = Project(app)
        project.play = True
        project.time = 0
        project.fps = 30

        project.camera = Camera()
        project.camera.translate(0, 0, -3)

        project.texture = os.path.join(os.getcwd(), resources, "default.jpg")
        project.audio = ""

        project.values = {}

        project.code = CodeInfo("""uniform float Size;\nuniform bool Mirror;\n\nRay camera() {\n\treturn camPerspective(1.0);\n}\nvec3 distort(vec3 p) {\n\tif (Mirror) p = opMirror(p, 0.1);\n\treturn distortSin(p, 0.5, 1.5, vec3(time, 0.0, 0.0));\n}\nfloat map(vec3 p) {\n\treturn sdSphere(distort(p), 1.0 + Size);\n}\nvec4 display(float depth, float dist, vec3 pos, vec3 norm) {\n\tif (dist >= RM_STOP_DIST) {\n\t\treturn vec4(0.0);\n\t} else {\n\t\treturn sample(ctob(distort(pos)));\n\t}\n}""")

        project.script = """
print("Hello rdapp!")\n\ndef update(dt):\n\tpass
        """

        project.backup_code = None
        project.backup_values = None

        project.create_values()
        return project


    def create_values(self):
        new_vals = {}
        for u in self.code.uniforms:
            if not u.name in self.values or self.values[u.name].type != u.type:
                new_vals[u.name] = Value(self, u.name, u.type, u.ndim)
            else:
                new_vals[u.name] = self.values[u.name]
        self.values = new_vals

    def get_uniforms(self):
        uniforms = {
            "time": self.time,
            "fps": self.fps,
            "camera_mat": self.camera.get(),
            "sound": self.app.sound
        }
        for val in self.values:
            uniforms[val] = self.values[val].get_uniform()
        return uniforms

    def restore_code(self):
        self.code = self.backup_code
        self.values = self.backup_values

    def set_code(self, code):
        self.backup_code = self.code
        self.backup_values = self.values
        self.code = CodeInfo(code)
        self.create_values()

    def set_frame(self, frame):
        self.time = frame/self.fps

    def get_frame(self):
        return self.time * self.fps

    def set_time(self, time):
        self.time = time

    def get_time(self):
        return self.time

    def set_fps(self, fps):
        self.fps = fps

    def get_fps(self):
        return self.fps


class Value:
    def __init__(self, project, name, type, ndim, base=None, track=None, use_track=None):
        self._project = project
        self._name = name
        self.type = type
        self.ndim = ndim
        if base:
            self.set_base(base)
        else:
            self.set_base(self.default_base())
        if track:
            self._track = track
        else:
            self._track = self.default_track()
        if use_track is not None:
            self._use_track = use_track
        else:
            self._use_track = (type == "float" and ndim == 1)

    def process(self, val):
        if self.ndim == 1:
            if self.type == "float":
                return float(val)
            if self.type == "int":
                return int(val)
            return val
        if self.type == "float":
            return np.float64(val)
        if self.type == "int":
            return np.int64(val)
        return val

    def save(self):
        out = {}
        out["_name"] = self._name
        out["type"] = self.type
        out["ndim"] = self.ndim
        if self.ndim > 1:
            out["_base"] = list(self._base)
        else:
            out["_base"] = self._base
        out["_track"] = self._track.save()
        out["_use_track"] = self._use_track
        return out

    @staticmethod
    def load(project, data):
        val = Value(project, data["_name"], data["type"], data["ndim"], data["_base"], Track.load(data["_track"]), data["_use_track"])
        return val

    def default_base(self):
        if self.type == "float" or self.type == "int":
            if self.ndim > 1:
                return [0 for i in range(self.ndim)]
            else: return 0
        elif self.type == "bool":
            return False

    def default_track(self):
        return Track()

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, val):
        self.set_value(val)

    def get_value(self):
        if self._use_track:
            if not self._track.empty():
                return self.get_track()
        return self.get_base()

    def set_value(self, val):
        self.set_base(val)

    def get_base(self):
        return self._base

    def set_base(self, val):
        self._base = self.process(val)

    def get_track_at(self, time):
        return self._track.value(time)

    def set_track_at(self, time, val):
        self._track.add_keyframe(time, val)

    def get_track(self):
        return self.get_track_at(self._project.time)

    def set_track(self):
        return self.set_track_at(self._project.time)

    def use_track(self, val=True):
        self._use_track = val

    def get_uniform(self):
        if self.ndim > 1:
            return tuple(self.value)
        return self.value


class CodeInfo:
    def __init__(self, code):
        self.code = code
        self.uniforms = self.find_uniforms(self.code)

    def find_uniforms(self, code):
        uniforms = []
        lines = code.split("\n")
        for l in lines:
            line = l.split(" ")
            if line[0] == "uniform":
                type = line[1]
                name = line[2].split(";")[0]
                if type == "float":
                    uniforms.append(Uniform("float", 1, name))
                elif type == "vec2":
                    uniforms.append(Uniform("float", 2, name))
                elif type == "vec3":
                    uniforms.append(Uniform("float", 3, name))
                elif type == "vec4":
                    uniforms.append(Uniform("float", 4, name))
                elif type == "bool":
                    uniforms.append(Uniform("bool", 1,  name))
                elif type == "int":
                    uniforms.append(Uniform("int", 1,  name))
                else:
                    print("Uniforms of type {} are not supported".format(type))
        return uniforms


class Uniform:
    def __init__(self, type, ndim, name):
        self.type = type
        self.ndim = ndim
        self.name = name


class RenderConfig:
    def __init__(self):
        self.size = (1024, 1024)
        self.max_patch = 512
        self.steps = 1024*4
        self.steps_max = 256
        self.step_scale = 100
        self.stop_dist = 100
        self.max_depth = 10
        self.min_depth = 0.001
        self.aa = 2
        self.path = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/render/auto"
        self.snap_path = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/snap"
        self.frames = (0, 100)
        self.preview_max_size = 1024
        self.mp4 = False

    def checkpaths(self):
        if not os.path.exists(self.path) and self.path != QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/render/auto":
            self.path = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/render/auto"
        if not os.path.exists(self.snap_path):
            self.snap_path = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/snap"
    
    def save(self):
        data = {}
        data["size"] = self.size
        data["max_patch"] = self.max_patch
        data["steps"] = self.steps
        data["steps_max"] = self.steps_max
        data["step_scale"] = self.step_scale
        data["stop_dist"] = self.stop_dist
        data["max_depth"] = self.max_depth
        data["min_depth"] = self.min_depth
        data["aa"] = self.aa
        data["path"] = self.path
        data["snap_path"] = self.snap_path
        data["frames"] = self.frames
        data["preview_max_size"] = self.preview_max_size
        data["mp4"] = self.mp4

        return data

    @staticmethod
    def default():
        config = RenderConfig()
        config.checkpaths()
        return config

    @staticmethod
    def load(data):
        self = RenderConfig()
        if "size" in data: self.size = data["size"]
        if "max_patch" in data: self.max_patch = data["max_patch"]
        if "steps" in data: self.steps = data["steps"]
        if "steps_max" in data: self.steps_max = data["steps_max"]
        if "step_scale" in data: self.step_scale = data["step_scale"]
        if "stop_dist" in data: self.stop_dist = data["stop_dist"]
        if "max_depth" in data: self.max_depth = data["max_depth"]
        if "min_depth" in data: self.min_depth = data["min_depth"]
        if "aa" in data: self.aa = data["aa"]
        if "path" in data: self.path = data["path"]
        if "snap_path" in data: self.snap_path = data["snap_path"]
        if "frames" in data: self.frames = data["frames"]
        if "preview_max_size" in data: self.preview_max_size = data["preview_max_size"]
        if "mp4" in data: self.mp4 = data["mp4"]

        self.checkpaths()
        return self


class LiveConfig:
    def __init__(self, app):
        self.app = app

        self.steps = 128
        self.step_scale = 10
        self.stop_dist = 100
        self.max_depth = 10
        self.min_depth = 0.001

        self.size = (512, 512)
        self.margins = 10

        self.clear = True
        self.downscale = 1

    def save(self):
        data = {}
        data["steps"] = self.steps
        data["step_scale"] = self.step_scale
        data["stop_dist"] = self.stop_dist
        data["max_depth"] = self.max_depth
        data["min_depth"] = self.min_depth
        data["size"] = self.size
        data["margins"] = self.margins
        data["clear"] = self.clear
        data["downscale"] = self.downscale
        return data

    @staticmethod
    def load(app, data):
        self = LiveConfig(app)
        if "steps" in data: self.steps = data["steps"]
        if "step_scale" in data: self.step_scale = data["step_scale"]
        if "stop_dist" in data: self.stop_dist = data["stop_dist"]
        if "max_depth" in data: self.max_depth = data["max_depth"]
        if "min_depth" in data: self.min_depth = data["min_depth"]
        if "size" in data: self.size = data["size"]
        if "margins" in data: self.margins = data["margins"]
        if "clear" in data: self.clear = data["clear"]
        if "downscale" in data: self.downscale = data["downscale"]
        return self

    @staticmethod
    def default(app):
        return LiveConfig(app)

    @property
    def viewport(self):
        viewport_size = utils.fit(
            self.app.render_config.size, (self.size[0]-self.margins*2, self.size[1]-self.margins*2))
        viewport_pos = (self.size[0] - viewport_size[0]) / 2, (self.size[1] - viewport_size[1]) / 2
        return viewport_pos + viewport_size

    def get_uniforms(self):
        uniforms={}
        viewport = self.viewport
        uniforms["render_size"] = viewport[2], viewport[3]
        uniforms["patch_size"] = self.size
        uniforms["patch_pos"] = -viewport[0], -viewport[1]
        return uniforms

class AppConfig:
    def __init__(self):
        self.theme = 70
        self.script_startup = False

    def save(self):
        return {"theme": self.theme, "script_startup": self.script_startup}

    @staticmethod
    def default():
        return AppConfig()

    @staticmethod
    def load(data):
        self = AppConfig()
        if "theme" in data: self.theme = data["theme"]
        if "script_startup" in data: self.script_startup = data["script_startup"]
        return self
