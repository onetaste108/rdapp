import pydub
import simpleaudio
import os
from rdapp.qtmic import AudioInput


class Audio:
    def __init__(self, app):
        self.app = app
        self.segment = None
        self.input = None
        self.playback = None

    def release(self):
        self.stop()
        self.segment = None
        if self.input:
            self.input.stop()
        self.input = None        

    def load(self, file, print_err=False):
        self.release()
        try:
            id = int(file)
            try:
                input = AudioInput(id)
                self.input = input
                return True
            except Exception as err:
                if print_err:
                    print("Error setting audio '{}': {}".format(file, err))
                return False
        except:
            try:
                segment = pydub.AudioSegment.from_file(file)
                self.segment = segment
                return True
            except Exception as err:
                if print_err:
                    print("Error setting audio '{}': {}".format(file, err))
                return False

    def stop(self):
        if self.playback:
            self.playback.stop()
            self.playback = None

    def _play(self, seg):
        self.playback = simpleaudio.play_buffer(
            seg.raw_data,
            num_channels=seg.channels,
            bytes_per_sample=seg.sample_width,
            sample_rate=seg.frame_rate
        )

    def play_from(self, time):
        if self.segment:
            time = max(0, min(len(self.segment)-1, int(time*1000)))
            self.stop()
            self._play(self.segment[time:])

    def play(self):
        self.play_from(self.app.time)

    @property
    def frame(self):
        if self.segment:
            time0 = self.app.time
            time1 = self.app.time + 1/self.app.fps
            time0 = max(0, min(len(self.segment)-1, int(time0*1000)))
            time1 = max(0, min(len(self.segment)-1, int(time1*1000)))
            return self.segment[time0:time1]
        if self.input:
            return self.input.frame
        return None

    @property
    def rms(self):
        frame = self.frame
        if frame:
            return frame.rms / frame.max_possible_amplitude
        return 0
            