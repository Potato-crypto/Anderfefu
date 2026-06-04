from Dvishok.Sprite.Sprite.SpriteSurface import SpriteSurface
from OpenGL.GL import *
import ctypes
from pyglm import glm


class Image(SpriteSurface):
    def __init__(self, width, height, camera, texture, x=0, y=0):
        super().__init__(width, height, camera, texture=texture, x=x, y=y)
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

        stride = 8 * 4  # 8 флоатов на 4 байта

        # позиции
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        #  (не перепутай пж_)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # UV
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def draw(self):
        self.shader.use()

        glActiveTexture(GL_TEXTURE0)

        self.texture.bind()

        glUniform1i(
            glGetUniformLocation(self.shader.program, "texture1"),
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