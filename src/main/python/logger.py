from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property
import sys

class Logger(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.terminal = sys.stdout
        self._log = ""
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        self.terminal.write(message)
        self._log += message

    def read(self):
        tmp = self._log
        self._log = ""
        return tmp

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    