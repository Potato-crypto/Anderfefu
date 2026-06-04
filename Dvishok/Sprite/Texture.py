from OpenGL.GL import *
from PIL import Image

class Texture:
    def __init__(self, path: str):
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        image = Image.open(path).convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.tobytes()
        self.width, self.height = image.size

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            self.width, self.height,
            0, GL_RGBA, GL_UNSIGNED_BYTE, img_data
        )

        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)