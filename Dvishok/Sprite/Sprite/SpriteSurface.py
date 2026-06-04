from OpenGL.GL import *
import numpy as np
import ctypes
from pyglm import glm
from Dvishok.Shaders.Shader import Shader
from Dvishok.Sprite.Rect import Rect
from Dvishok.Camera import Camera


class SpriteSurface:
    def __init__(self, width: int, height: int, camera: Camera, color=None, x=0, y=0, texture=None):
        self.width = width
        self.height = height
        self.camera = camera
        self.texture = texture
        self.x = x
        self.y = y

        if color is None:
            self.color = [1, 0, 0, 1]
        else:
            self.color = [c / 255.0 for c in color]

            if len(self.color) == 3:
                self.color.append(1.0)

        self.shader = Shader(
            "Dvishok/Shaders/surface/vShader.glsl",
            "Dvishok/Shaders/surface/fShader.glsl"
        )

        self.rect = Rect(self.camera)
        self.rect.scale(glm.vec3(self.width, self.height, 0))
        self.rect.x += x
        self.rect.y += y

        self.vertices = np.array([
            # x  y  z      r              g              b              a          u    v

            1, 1, 0.0, self.color[0], self.color[1], self.color[2], self.color[3], 1.0, 0.0,
            1, 0, 0.0, self.color[0], self.color[1], self.color[2], self.color[3], 1.0, 1.0,
            0, 0, 0.0, self.color[0], self.color[1], self.color[2], self.color[3], 0.0, 1.0,
            0, 1, 0.0, self.color[0], self.color[1], self.color[2], self.color[3], 0.0, 0.0

        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 3,
            1, 2, 3
        ], dtype=np.uint32)

        self._setup_buffers()

    def _setup_buffers(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        stride = 9 * 4

        # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # color rgba
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # uv
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(28))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader.use()

        if self.texture:
            self.texture.bind()
            glUniform1i(
                glGetUniformLocation(self.shader.program, "useTexture"),
                1
            )
        else:
            glUniform1i(
                glGetUniformLocation(self.shader.program, "useTexture"),
                0
            )

        self.shader.set_mat4(
            "model",
            glm.value_ptr(self.rect.getMVP())
        )

        glBindVertexArray(self.VAO)

        glDrawElements(
            GL_TRIANGLES,
            6,
            GL_UNSIGNED_INT,
            None
        )

        glBindVertexArray(0)