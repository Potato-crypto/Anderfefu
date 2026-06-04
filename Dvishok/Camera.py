from pyglm import glm

class Camera:
    def __init__(self, width, height):
        self.OrthoMatrix = None
        self.width = width
        self.height = height

        self.rebuildOrthoMatrix()

    def getOrthoMatrix(self) -> glm.mat4:
        return self.OrthoMatrix

    def rebuildOrthoMatrix(self):
        self.OrthoMatrix = glm.ortho(0, self.width, self.height, 0)