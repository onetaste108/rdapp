class Mouse:
    def __init__(self):
        self.x, self.y, self.px, self.py, self.dx, self.dy = 0, 0, 0, 0, 0, 0
    def pressed(self, x, y):
        self.x, self.y, self.px, self.py, self.dx, self.dy = x, y, x, y, 0, 0
    def moved(self, x, y):
        self.px, self.py = self.x, self.y
        self.x, self.y = x, y
        self.dx, self.dy = self.x - self.px, self.y-self.py
        