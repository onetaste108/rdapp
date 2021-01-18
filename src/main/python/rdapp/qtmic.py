from PyQt5.QtMultimedia import QAudioInput, QAudioFormat, QAudioDeviceInfo
from PyQt5.QtCore import QIODevice, Qt
from pydub import AudioSegment

import numpy as np

class AudioInput:

    def __init__(self, id, dt = 1/120):
        
        adi = QAudioDeviceInfo.availableDevices(0)[id]

        pfmt = QAudioFormat()
        pfmt.setSampleRate(44100)
        pfmt.setChannelCount(1)
        pfmt.setSampleSize(16)
        pfmt.setByteOrder(QAudioFormat.LittleEndian)
        pfmt.setSampleType(QAudioFormat.SignedInt)

        fmt = adi.nearestFormat(pfmt)
        BUFFER = fmt.sampleSize()//8 * fmt.channelCount() * int(fmt.sampleRate() * dt)

        self.inp = QAudioInput(adi, fmt)
        self.inp.setBufferSize(BUFFER)

        self.dev = AudioDevice()
        self.dev.fmt = fmt
        self.dev.buffer_size = self.inp.bufferSize()
        self.dev.open(QIODevice.WriteOnly)
        self.inp.start(self.dev)


    @property
    def frame(self):
        return self.dev.data

    def stop(self):
        self.inp.stop()
        self.dev.close()


class AudioDevice(QIODevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = AudioSegment.silent(1000//120)
        self.fmt = None
        self.buffer_size = None

    def writeData(self, data):
        self.data = AudioSegment(
            data=data,
            sample_width=self.fmt.sampleSize()//8,
            frame_rate=self.fmt.sampleRate(),
            channels=self.fmt.channelCount()
        )
        return self.buffer_size
