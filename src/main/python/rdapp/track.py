from PyQt5.QtCore import QEasingCurve, QPointF


class Track:
    def __init__(self):
        self.keyframes = []
        self.viewport = [0,10,1,-1]

    def save(self):
        out = {}
        out["keyframes"] = [k.save() for k in self.keyframes]
        out["viewport"] = list(self.viewport)
        return out

    @staticmethod
    def load(data):
        track = Track()
        track.keyframes = [Keyframe.load(k) for k in data["keyframes"]]
        track.viewport = data["viewport"]
        return track

    def empty(self):
        return len(self.keyframes) == 0

    def add(self, time=0, value=0, in_infl=0.25, in_vel=0, out_infl=0.25, out_vel=0):
        k = Keyframe(time, value, in_infl, in_vel, out_infl, out_vel)
        self.keyframes.append(k)
        self.sort()
        return k

    def remove(self, k):
        self.keyframes.remove(k)

    def sort(self):
        self.keyframes.sort(key=lambda x: x.time)

    def prev(self, k):
        idx = self.keyframes.index(k)
        if idx > 0:
            return self.keyframes[idx-1]
        else:
            return None

    def next(self, k):
        idx = self.keyframes.index(k)
        if idx < len(self.keyframes)-1:
            return self.keyframes[idx+1]
        else:
            return None

    def neighbours(self, k):
        return self.prev(k), self.next(k)

    def time_dist(self, k1, k2):
        return k2.time - k1.time

    def get_bezier(self, k):
        prev = self.prev(k)
        if prev:
            in_x = lerp(k.time, prev.time, k.in_infl)
            in_y = k.value + k.in_vel * (k.time - prev.time) * k.in_infl
        else:
            in_x, in_y = k.time, k.value
        next = self.next(k)
        if next:
            out_x = lerp(k.time, next.time, k.out_infl)
            out_y = k.value + k.out_vel * (next.time - k.time) * k.out_infl
        else:
            out_x, out_y = k.time, k.value
        return [[k.time, k.value], [in_x, in_y], [out_x, out_y]]

    def time_select(self, time_in, time_out):
        sel = []
        first = True
        last = False
        for i, k in enumerate(self.keyframes):
            if k.time >= time_in and k.time <= time_out:
                if first:
                    if i > 0:
                        sel.append(self.keyframes[i-1])
                    first = False
                    last = True
                sel.append(k)
            else:
                if last:
                    sel.append(k)
                    last = False
                    break

        return sel

    def get_bezier_for_time(self, time_in, time_out):
        sel = self.time_select(time_in, time_out)
        pts = []
        for k in sel:
            pts.append(self.get_bezier(k))
        return pts

    def set_time(self, k, time):
        k.time = time
        self.sort()

    def set_value(self, k, value):
        k.value = value

    def set_in_infl(self, k, in_infl):
        in_infl = max(min(in_infl, 1), 0)
        k.in_infl = in_infl

    def set_out_infl(self, k, out_infl):
        out_infl = max(min(out_infl, 1), 0)
        k.out_infl = out_infl

    def set_in_vel(self, k, in_vel):
        k.in_vel = in_vel

    def set_out_vel(self, k, out_vel):
        k.out_vel = out_vel

    def set_pos_from_bezier(self, k, time, value):
        self.set_time(k, time)
        self.set_value(k, value)

    def set_in_point_from_bezier(self, k, x, y, mirror_x=False, mirror_y=False):
        # print(x, y)
        prev = self.prev(k)
        if not prev:
            # raise Exception("Keyframe Error: no prev keyframe")
            in_infl = k.in_infl
        else:
            in_infl = (k.time - x) / (k.time - prev.time)
        in_vel = (y - k.value) / (k.time - x)
        self.set_in_infl(k, in_infl)
        self.set_in_vel(k, in_vel)
        if mirror_x:
            self.set_out_infl(k, in_infl)
        if mirror_y:
            self.set_out_vel(k, -in_vel)

    def set_out_point_from_bezier(self, k, x, y, mirror_x=False, mirror_y=False):
        next = self.next(k)
        if not next:
            # raise Exception("Keyframe Error: no next keyframe")
            out_infl = k.out_infl
        else:
            out_infl = (x - k.time) / (next.time - k.time)
        out_vel = (k.value - y) / (k.time - x)
        self.set_out_infl(k, out_infl)
        self.set_out_vel(k, out_vel)
        if mirror_x:
            self.set_in_infl(k, out_infl)
        if mirror_y:
            self.set_in_vel(k, -out_vel)

    def value(self, time):
        if len(self.keyframes) == 0:
            # raise Exception("No Keyframes!")
            return 0
        elif len(self.keyframes) == 1:
            return self.keyframes[0].value
        else:
            for i, k in enumerate(self.keyframes):
                if k.time > time:
                    if i == 0:
                        return k.value
                    else:
                        key1 = self.get_bezier(self.keyframes[i-1])
                        key2 = self.get_bezier(k)
                        return getBzY(key1[0], key1[2], key2[1], key2[0], time)
            return self.keyframes[-1].value





class Keyframe:
    def __init__(self, time=0, value=0, in_infl=0.25, in_vel=0, out_infl=0.25, out_vel=0):
        self.time = time
        self.value = value
        self.in_infl = in_infl
        self.in_vel = in_vel
        self.out_infl = out_infl
        self.out_vel = out_vel

    def save(self):
        out = {}
        out["time"] = self.time
        out["value"] = self.value
        out["in_infl"] = self.in_infl
        out["in_vel"] = self.in_vel
        out["out_infl"] = self.out_infl
        out["out_vel"] = self.out_vel
        return out

    @staticmethod
    def load(data):
        return Keyframe(data["time"], data["value"], data["in_infl"], data["in_vel"], data["out_infl"], data["out_vel"])

def lerp(a, b, c):
    return (b-a)*c+a

def getBzY(p1, p1o, p2i, p2, t):
    width = p2[0]-p1[0]
    height = p2[1]-p1[1]
    mX1 = (p1o[0]-p1[0])/width
    mY1 = (p1o[1]-p1[1])/height
    mX2 = (width+(p2i[0]-p2[0]))/width
    mY2 = (height+(p2i[1]-p2[1]))/height
    x = (t-p1[0])/width
    curve = QEasingCurve(QEasingCurve.BezierSpline)
    curve.addCubicBezierSegment(
        QPointF(mX1, mY1), QPointF(mX2, mY2), QPointF(1, 1))
    return p1[1]+curve.valueForProgress(x)*height
