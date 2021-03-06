
from rdapp.program import Texture
from rdapp.project import Project, RenderConfig, LiveConfig, AppConfig
from rdapp.writer import Writer
from rdapp.reader import Reader
from rdapp.audio import Audio
from rdapp.builder import Builder
from rdapp.blitter import Blitter
from rdapp.scanner import Scanner
from rdapp.blitter import Blitter
from rdapp.renderer import Renderer, RenderJob
from rdapp.liver import Liver
from rdapp import noise
import moderngl
import json
import os


class App:
    def __init__(self, resources="", project = None):
        super().__init__()
        self.version = [0,7,0]
        self.resources = resources
        self.builder = Builder(resources+"/shaders")
        self.project = None
        self.render_config = None
        self.live_config = None
        self.reader = Reader(self)
        self.writer = Writer()
        self.audio = Audio(self)

        self.ctx = None
        self.screen = None
        self.texture = None
        self.blitter = None
        self.liver = None
        self.renderer = None
        self.scanner = None

        self._render_requested = False
        self._render_stop_requested = False
        self._render_requests = []
        self._scan_requested = False
        self._scan_stop_requested = False
        self._live_build_requested = False
        self._code_update_requested = False

        self._state = "LIVE"
        self.state = self._state
        self._play = True
        self.update = None

        self.states = {
            "project_loaded": False
        }

        self.project_path = None
        if project is not None:
            self.load_project(project)
        else:
            self.default_project()


    def init(self):
        self.ctx = moderngl.create_context()
        self.texture = Texture(self.ctx)
        self.blitter = Blitter(self)
        self.liver = Liver(self)
        self.renderer = Renderer(self)
        self.scanner = Scanner(self)


    def load_project(self, path=None):
        try:
            with open(path, "r") as f:
                data = json.loads(f.read())
            if data["version"] != self.version:
                raise ValueError("Project version {}.{}.{} is not compatable with app version {}.{}.{}".format(*data["version"], *self.version))
            self.project = Project.load(self, data["project"])
            self.render_config = RenderConfig.load(data["render_config"])
            self.live_config = LiveConfig.load(self, data["live_config"])
            self.app_config = AppConfig.load(data["app_config"])
            self.project_path = path
            self.init_project()
            print("Project Loaded: "+path)
        except Exception as err:
            print("Error loading project: {}".format(err))
            self.default_project()

    def default_project(self):
        self.project = Project.default(self, self.resources)
        self.render_config = RenderConfig.default()
        self.live_config = LiveConfig.default(self)
        self.app_config = AppConfig.default()
        self.project_path = None
        print("Default Project Loaded")
        self.init_project()

    def init_project(self):
        self._live_build_requested = True
        self._code_update_requested = True
        self.update = None
        self.set_texture(self.project.texture)
        self.set_audio(self.project.audio)
        self.states["project_loaded"] = True
        if self.get_script_startup():
            self.run_script(self.project.script)

    def save(self):
        out = {}
        out["version"] = self.version
        out["project"] = self.project.save()
        out["render_config"] = self.render_config.save()
        out["live_config"] = self.live_config.save()
        out["app_config"] = self.app_config.save()
        json_out = json.dumps(out, indent=4)
        return json_out

    def save_as(self, path):
        with open(path, "w") as f:
            f.write(self.save())
        self.project_path = path
        print("Project Saved: "+path)

    def resize(self, w, h):
        self.live_config.size = w, h

    def _update(self, dt):
        if self._state == "LIVE":
            if self._play:
                self.time += dt

        if self.update:
            try:
                self.update(dt)
            except Exception as err:
                print("Error in update loop: {}".format(err))
                self.update = None

    def sync(self, dt=None):
        if not dt:
            dt = 1 / self.fps

        if self._render_requested:
            self._render_requested = False
            for req in self._render_requests:
                self.renderer.add_queue(req)
            self._render_requests = []
            self._state = "RENDER"
            self.renderer.finished = False

        if self._scan_requested:
            self.scanner.start()
            self._state = "SCAN"
            self._scan_requested = False
            self.scanner.finished = False
        
        if self._render_stop_requested:
            self._render_stop_requested = False
            self.renderer.cancel = True

        if self._scan_stop_requested:
            self._scan_stop_requested = False
            self.scanner.cancel = True


        if self._state == "LIVE":
            self._update(dt)
            self.reader.update(self.time)
            self.texture.use()
            self.liver.sync()


    def draw(self):
        self.screen = self.ctx.detect_framebuffer()

        if self._state == "RENDER":

            self.renderer.advance()
            if self.renderer.finished:
                self._state = "LIVE"

        if self._state == "SCAN":

            self.scanner.advance()
            if self.scanner.finished:
                self._state = "LIVE"

        elif self._state == "LIVE":

            self.liver.render()

    def _code_accepted(self):
        self._code_update_requested = False
        pass

    def _code_rejected(self):
        self.project.restore_code()
        

    # API

    def play(self):
        self._play = True
        self.audio.play_from(self.time)

    def stop(self):
        self._play = False
        self.audio.stop()

    @property
    def playing(self):
        if self._state == "RENDER":
            return True
        return self._play

    @property
    def rendering(self):
        return self._state == "RENDER"

    def render(self):
        self._render_requested = True
        self._render_requests.append(
            RenderJob(self.project, self.render_config))

    def scan(self):
        self._scan_requested = True

    def snap(self):
        self._render_requested = True
        self._render_requests.append(
            RenderJob(self.project, self.render_config, [self.frame], True))

    def stop_render(self):
        if self._state == "RENDER":
            self._render_stop_requested = True

    def stop_scan(self):
        if self._state == "SCAN":
            self._scan_stop_requested = True
            
    def get(self, name):
        if name in self.project.values:
            return self.project.values[name]
        else:
            raise Exception("No value \"{}\" found".format(name))

    def set_shader(self, code):
        self._code_update_requested = True
        self._live_build_requested = True
        self.project.set_code(code)

    def set_texture(self, path, print_err=True):
        # print("PATH", path)
        if not path or path == "":
            self.reader.release()
            self.project.texture = ""
            return
        success = self.reader.load(path, print_err)
        if success:
            print("Video set: {}".format(path))
            self.project.texture = path
            if self.reader.fps:
                self.fps = self.reader.fps
                self.time = 0
            else:
                self.fps = self.project.fps
        else:
            if path != self.resources + "/default.jpg":
                self.set_texture(self.resources + "/default.jpg", print_err)
            
    def set_audio(self, path, print_err=True):
        if not path or path == "":
            self.audio.stop()
            self.audio.release()
            self.project.audio = ""
            return
        success = self.audio.load(path, print_err)
        if success:
            print("Audio set: {}".format(path))
            self.project.audio = path
            if self.playing:
                self.audio.play()

    def set_file(self, path):
        vid = True
        aud = True
        ext = os.path.splitext(path)[-1].lower()
        if ext in [".jpg", ".gif", ".tif", ".tiff", ".jpeg", ".webp", ".png"]: aud = False
        if ext in [".mp3", ".wav", ".ogg", ".flac"]: vid = False
        if vid: self.set_texture(path, False)
        if aud: self.set_audio(path, False)

    def run_script(self, code):
        try:
            scope = {
                "app": self,
                "update": None
                }
            exec(code, scope)
            update = scope["update"]
            if callable(update):
                self.update = update
        except Exception as err:
            print("Error running script: {}".format(err))
        self.project.script = code

    # Properties

    @property
    def time(self):
        return self.project.get_time()

    @time.setter
    def time(self, time):
        self.project.set_time(time)

    @property
    def frame(self):
        return self.project.get_frame()

    @frame.setter
    def frame(self, frame):
        self.project.set_frame(frame)

    @property
    def fps(self):
        return self.project.get_fps()

    @fps.setter
    def fps(self, fps):
        self.project.set_fps(fps)

    @property
    def cam(self):
        return self.project.camera

    @cam.setter
    def cam(self, cam):
        self.project.camera = cam

    @property
    def data(self):
        return self.project.data

    @property
    def sound(self):
        return self.audio.rms

    @property
    def image(self):
        return self.reader.image

    @property
    def color(self):
        return self.reader.color

    @property
    def pcolor(self):
        return self.reader.pcolor

    # Render Config API

    def set_render_size(self, val):
        self.render_config.size = val

    def get_render_size(self):
        return self.render_config.size

    def set_render_max_patch(self, val):
        self.render_config.max_patch = val

    def get_render_max_patch(self):
        return self.render_config.max_patch

    def set_render_steps(self, val):
        self.render_config.steps = val

    def get_render_steps(self):
        return self.render_config.steps

    def set_render_steps_max(self, val):
        self.render_config.steps_max = val

    def get_render_steps_max(self):
        return self.render_config.steps_max

    def set_render_step_scale(self, val):
        self.render_config.step_scale = val

    def get_render_step_scale(self):
        return self.render_config.step_scale

    def set_render_stop_dist(self, val):
        self.render_config.stop_dist = val

    def get_render_stop_dist(self):
        return self.render_config.stop_dist

    def set_render_max_depth(self, val):
        self.render_config.max_depth = val

    def get_render_max_depth(self):
        return self.render_config.max_depth

    def set_render_min_depth(self, val):
        self.render_config.min_depth = val

    def get_render_min_depth(self):
        return self.render_config.min_depth

    def set_render_aa(self, val):
        self.render_config.aa = val

    def get_render_aa(self):
        return self.render_config.aa

    def set_render_path(self, val):
        self.render_config.path = val

    def get_render_path(self):
        return self.render_config.path

    def set_snap_path(self, val):
        self.render_config.snap_path = val

    def get_snap_path(self):
        return self.render_config.snap_path

    def set_render_frames(self, val):
        val[1] = max(val[1], val[0])
        self.render_config.frames = val

    def get_render_frames(self):
        return self.render_config.frames

    def set_render_preview_max_size(self, val):
        self.render_config.preview_max_size = val

    def get_render_preview_max_size(self):
        return self.render_config.preview_max_size

    def set_render_mp4(self, val):
        self.render_config.mp4 = val

    def get_render_mp4(self):
        return self.render_config.mp4

    def set_render_depth(self, val):
        self.render_config.depth = val

    def get_render_depth(self):
        return self.render_config.depth

    def set_render_depth_mask(self, val):
        self.render_config.depth_mask = val

    def get_render_depth_mask(self):
        return self.render_config.depth_mask

    def set_render_scan_box(self, val):
        self.render_config.scan_box = val

    def get_render_scan_box(self):
        return self.render_config.scan_box

    def set_render_scan_res(self, val):
        self.render_config.scan_res = val

    def get_render_scan_res(self):
        return self.render_config.scan_res
    


    # Live Config API

    def set_live_steps(self, val):
        self._live_build_requested = True
        self.live_config.steps = val

    def get_live_steps(self):
        return self.live_config.steps

    def set_live_step_scale(self, val):
        self._live_build_requested = True
        self.live_config.step_scale = val

    def get_live_step_scale(self):
        return self.live_config.step_scale

    def set_live_stop_dist(self, val):
        self._live_build_requested = True
        self.live_config.stop_dist = val

    def get_live_stop_dist(self):
        return self.live_config.stop_dist

    def set_live_max_depth(self, val):
        self._live_build_requested = True
        self.live_config.max_depth = val

    def get_live_max_depth(self):
        return self.live_config.max_depth

    def set_live_min_depth(self, val):
        self._live_build_requested = True
        self.live_config.min_depth = val

    def get_live_min_depth(self):
        return self.live_config.min_depth

    def set_live_size(self, val):
        self._live_build_requested = True
        self.live_config.size = val

    def get_live_size(self):
        return self.live_config.size

    def set_live_margins(self, val):
        self._live_build_requested = True
        self.live_config.margins = val

    def get_live_margins(self):
        return self.live_config.margins

    def set_live_clear(self, val):
        self._live_build_requested = True
        self.live_config.clear = val

    def get_live_clear(self):
        return self.live_config.clear

    def set_live_downscale(self, val):
        val = max(1, val)
        self.live_config.downscale = val

    def get_live_downscale(self):
        return self.live_config.downscale


    def set_script_startup(self, x):
        self.app_config.script_startup = x

    def get_script_startup(self):
        return self.app_config.script_startup