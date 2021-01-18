from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property
import math
import utils

class TimelineModel(QtCore.QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.value = None

        self._xIn = 0
        self._xOut = 10
        self._yIn = 1
        self._yOut = -1
        self._fps = 30
        self._time = 1
        self._snapTime = True
        self._visible = False

        self.xInChanged.connect(lambda x: self.set_value_viewport(x, 0))
        self.xOutChanged.connect(lambda x: self.set_value_viewport(x, 1))
        self.yInChanged.connect(lambda x: self.set_value_viewport(x, 2))
        self.yOutChanged.connect(lambda x: self.set_value_viewport(x, 3))

    def set_value(self, value):
        self.value = value
        self.set_track(self.value._track)

    def set_value_viewport(self, val, pos):
        if self.value is not None:
            self.value._track.viewport[pos] = val

    def set_track(self, track):
        self.beginResetModel()
        self.track = track
        self.keyframes = self.track.keyframes.copy()

        self.endResetModel()
        self.setGrid(*track.viewport)
        self.pathChanged.emit()


    def rowCount(self, parent=QtCore.QModelIndex()):
        if not self.value: return 0
        return len(self.track.keyframes)

    def data(self, index, role):
        k = self.keyframes[index.row()]
        if role == 0:
            return self.track.get_bezier(k)
        if role == 1:
            return k in self.selection

    def roleNames(self):
        return {
            0: b"keyframe",
            1: b"selected"
        }

    @Slot(float, float)
    def zoom(self, x, y):
        keys = self.selection
        self.selection = []
        for k in keys:
            self.keyframeChanged(k)

    def keyframeChanged(self, keyframe):
        idx = self.keyframes.index(keyframe)
        self.dataChanged.emit(self.index(idx), self.index(idx))

    @Slot(int)
    def removeKeyframe(self, id):
        self.beginRemoveRows(QtCore.QModelIndex(),
                             id, id)
        keyframe = self.keyframes[id]
        neighbors = self.track.neighbours(keyframe)
        self.track.remove(keyframe)
        self.keyframes.remove(keyframe)
        self.endRemoveRows()
        for k in neighbors:
            if k:
                self.keyframeChanged(k)
        self.pathChanged.emit()

    @Slot(float, float)
    def addKeyframe(self, x, y):
        if not self.value: return
        self.beginInsertRows(QtCore.QModelIndex(),
                             self.rowCount(), self.rowCount())
        keyframe = self.track.add(x, y)
        self.keyframes.append(keyframe)
        self.endInsertRows()
        for k in self.track.neighbours(keyframe) + (keyframe, ):
            if k:
                self.keyframeChanged(k)
        self.pathChanged.emit()

    @Slot(int, float, float)
    def moveKeyframe(self, idx, x, y):
        if self._snapTime:
            x = math.floor(x*self._fps)/self._fps
        keyframe = self.keyframes[idx]
        self.track.set_pos_from_bezier(keyframe, x, y)
        for k in self.track.neighbours(keyframe) + (keyframe, ):
            if k:
                self.keyframeChanged(k)
        self.pathChanged.emit()

    @Slot(int, str)
    def setValue(self, idx, value):
        val = utils.eval_float(value)
        if val is not None:
            self.moveKeyframe(idx, self.keyframes[idx].time, val)
        pass

    @Slot(int, float, float, bool)
    def moveInp(self, idx, x, y, mirror):
        keyframe = self.keyframes[idx]
        self.track.set_in_point_from_bezier(keyframe, x, y, mirror, mirror)
        for k in self.track.neighbours(keyframe) + (keyframe, ):
            if k:
                self.keyframeChanged(k)
        self.pathChanged.emit()

    @Slot(int, float, float, bool)
    def moveOut(self, idx, x, y, mirror):
        # print(x, y)
        keyframe = self.keyframes[idx]
        self.track.set_out_point_from_bezier(keyframe, x, y, mirror, mirror)
        for k in self.track.neighbours(keyframe) + (keyframe, ):
            if k:
                self.keyframeChanged(k)
        self.pathChanged.emit()

    @Slot(result=QtCore.QVariant)
    def getPath(self):
        if not self.value: return []
        return self.track.get_bezier_for_time(self.xIn, self.xOut)

    pathChanged = Signal()
    gridChanged = Signal()

    @Slot(float, float, float, float)
    def setGrid(self, xIn, xOut, yIn, yOut):
        self._xIn = xIn
        self._yIn = yIn
        self._xOut = xOut
        self._yOut = yOut
        self.xInChanged.emit(xIn)
        self.yInChanged.emit(yIn)
        self.xOutChanged.emit(xOut)
        self.yOutChanged.emit(yOut)
        self.gridChanged.emit()
        self.pathChanged.emit()

    visibleChanged = Signal(bool)
    @Property(bool, notify=visibleChanged)
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, val):
        self._visible = val
        self.visibleChanged.emit(self._visible)


    xInChanged = Signal(float)

    @Property(float, notify=xInChanged)
    def xIn(self):
        return self._xIn
    xOutChanged = Signal(float)

    @Property(float, notify=xOutChanged)
    def xOut(self):
        return self._xOut
    yInChanged = Signal(float)

    @Property(float, notify=yInChanged)
    def yIn(self):
        return self._yIn
    yOutChanged = Signal(float)

    @Property(float, notify=yOutChanged)
    def yOut(self):
        return self._yOut
    fpsChanged = Signal(float)

    @Property(float, notify=fpsChanged)
    def fps(self):
        return self._fps
    timeChanged = Signal(float)

    def set_fps(self, fps):
        self._fps = fps
        self.fpsChanged.emit(fps)

    @Property(float, notify=timeChanged)
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time
        self.timeChanged.emit(self._time)
