from OpenGL.GL import *
from Dvishok.Sprite.Sprite.Surface import Surface


class BackgroundSurface(Surface):
    def __init__(self, camera, width, height):
        super().__init__(camera, width, height)
        self.color = (0.2, 0.2, 0.2, 1.0)

    def set_color(self, color):
        self.color = (
            color[0] / 255.0,
            color[1] / 255.0,
            color[2] / 255.0,
            color[3] / 255.0 if len(color) > 3 else 1.0
        )

    def draw(self):
        glClearColor(*self.color)
        glClear(GL_COLOR_BUFFER_BIT)