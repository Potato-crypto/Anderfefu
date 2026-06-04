from Dvishok.Sprite.Model import Model
from Dvishok.Camera import Camera
from pyglm import glm

class Rect(Model):
    def __init__(self, camera: Camera, transform: glm.mat4 = None, rotation: glm.mat4 = None, scale: glm.mat4 = None):
        super().__init__(camera, transform, rotation, scale)

    @property
    def width(self):
        scale, orientation, translation, skew, perspective = self.decompose()
        return scale.x

    @property
    def height(self):
        scale, orientation, translation, skew, perspective = self.decompose()
        return scale.y

    @property
    def top_left(self):
        return self.x, self.y

    @property
    def top_right(self):
        return self.x + self.width, self.y

    @property
    def bottom_left(self):
        return self.x, self.y+self.height

    @property
    def bottom_right(self):
        return self.x+self.width, self.y+self.height

    @property
    def x(self):
        _, _, translation, _, _ = self.decompose()
        return translation.x

    @x.setter
    def x(self, value):
        current = self.x
        if value != current:
            delta = value - current
            self.translate_model(glm.vec3(delta, 0, 0))

    @property
    def y(self):
        _, _, translation, _, _ = self.decompose()
        return translation.y

    @y.setter
    def y(self, value):
        current = self.y
        if value != current:
            delta = value - current
            self.translate_model(glm.vec3(0, delta, 0))

    def scale(self, scale):
        self.scale_model(glm.vec3(scale[0], scale[1], 0))