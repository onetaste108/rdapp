import imageio
import numpy as np

class Reader:
    def __init__(self, app):
        self.app = app
        self.reader = None
        self._mode = None
        self._data = None
        self._color = None
        self._img_updated = False
        self._vid_last_frame = None
        self._vid_length = None
        self._vid_nframes = None
        self.fps = None

        self._MODE_IMG = 0
        self._MODE_VID = 1
        self._MODE_STREAM = 2

    @property
    def data(self):
        return self._data
        
    @data.setter
    def data(self, data):
        self._data = data
        self._pcolor = self._color
        self._color = None

    @property
    def image(self):
        if self.data is not None:
            return self.data
        return np.uint8([[[0, 0, 0, 0]]])
        
    @property
    def color(self):
        if self._color is None:
            self._color = np.average(self.image[:, :, : min(self.image.shape[-1], 3)]) / 255
        return self._color
        
    @property
    def pcolor(self):
        if self._pcolor is None:
            return self.color
        return self._pcolor

    def load(self, path, print_err=False):
        _vid_last_frame = None
        _vid_length = None
        _vid_nframes = None
        _fps = None
        _mode = None
        # try:
        #     id = int(path)
        #     path = "<video{}>".format(id)
        #     self._mode = self._MODE_STREAM
        # except:
        #     pass
        try:
            try:
                reader = imageio.get_reader(path)
            except:
                reader = imageio.get_reader(path, fps = 29.97)
            if path == "<screen>" or path.startswith("<video"):
                _mode = self._MODE_STREAM
            else:
                if reader.get_length() == 1:
                    _mode = self._MODE_IMG
                else:
                    try:
                        metadata = reader.get_meta_data()
                        fps = metadata["fps"]
                        length = metadata["duration"]
                        # print(length, fps)
                        if fps > 0:
                            _fps = fps
                        if length > 0 and fps > 0:
                            _mode = self._MODE_VID
                            _vid_nframes = int(length * fps)
                            _vid_length = length
                        else:
                            _mode = None
                    except Exception as err:
                        print(err)
                        pass
                        # _mode = self._MODE_STREAM
            self.release()
            self.reader = reader


            self._mode = _mode
            self._vid_last_frame = _vid_last_frame
            self._vid_length = _vid_length
            self._vid_nframes = _vid_nframes
            self.fps = _fps

            return True
        except Exception as err:
            if self._mode == self._MODE_STREAM:
                return True
            if (print_err):
                print("Error setting video: {}".format(err))
            return False

    def release(self):
        if self.reader:
            self.reader.close()
            self.reader = None
        self.data = None

    def get_data(self, frame):
        self.data = self.reader.get_data(frame)
    
    def set_tex(self):
        self.app.texture.set(self.data)

    def repeat_vid(self, frame):
        if frame < 0:
            frame = self._vid_nframes - (abs(frame) % self._vid_nframes)
        elif frame > self._vid_nframes:
            frame = frame % self._vid_nframes
        return frame

    def update(self, time):
        if self.reader is not None:
            if self._mode == self._MODE_STREAM:
                try:
                    self.data = self.reader.get_next_data()
                    self.set_tex()
                except Exception as err:
                    pass
                    # print(err)

            elif self._mode == self._MODE_IMG:
                    if self.data is None:
                        self.data = self.reader.get_data(0)
                        self.set_tex()

            elif self._mode == self._MODE_VID:
                frame = int(time * self.fps) 
                frame = self.repeat_vid(frame)
                if frame != self._vid_last_frame:
                    try:
                        self.data = self.reader.get_data(frame)
                        self.set_tex()
                        self._vid_last_frame = frame
                    except Exception as err:
                        print("Error reading video: {}".format(err))
                else:
                    pass
