from OpenGL.GL import *
import freetype
import numpy as np
import ctypes
from Dvishok.Shaders.Shader import Shader
from pyglm import glm
from Dvishok.Sprite.Font.Glyph import Glyph
from Dvishok.Sprite.Font.TextSurface import TextSurface

class Font:
    def __init__(self, path: str, size: int):
        self.face = freetype.Face(path)
        self.face.set_pixel_sizes(0, size)
        self.glyphs = {}

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 4, None, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.shader = Shader(
            "Dvishok/Shaders/fonts/text.vs",
            "Dvishok/Shaders/fonts/text.fs"
        )

    def load_glyph(self, char):
        if char in self.glyphs:
            return self.glyphs[char]

        self.face.load_char(char)
        bitmap = self.face.glyph.bitmap

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, bitmap.width, bitmap.rows, 0, GL_RED, GL_UNSIGNED_BYTE, bitmap.buffer)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glyph = Glyph(
            tex,
            (bitmap.width, bitmap.rows),
            (self.face.glyph.bitmap_left, self.face.glyph.bitmap_top),
            self.face.glyph.advance.x
        )
        self.glyphs[char] = glyph
        return glyph

    def render(self, text, color=(1,1,1), x=0, y=0, scale=1.0):
        return TextSurface(self, text, color, x=x, y=y, scale=scale)

    def draw(self, text_surface, x, y, width, height):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader.use()
        projection = glm.ortho(0.0, float(width), float(height), 0.0)
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        if len(text_surface.color) == 3:
            color = (*text_surface.color, 1.0)
        else:
            color = text_surface.color

        glUniform4f(
            glGetUniformLocation(self.shader.program, "textColor"),
            *color
        )
        glUniform1i(glGetUniformLocation(self.shader.program, "text"), 0)

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.VAO)

        start_x = x
        for char in text_surface.text:
            ch = self.load_glyph(char)
            xpos = start_x + ch.bearing[0] * text_surface.scale
            ypos = y + (ch.size[1] - ch.bearing[1]) * text_surface.scale
            w = ch.size[0] * text_surface.scale
            h = ch.size[1] * text_surface.scale

            vertices = np.array([
                xpos,     ypos - h,   0.0, 0.0,
                xpos,     ypos,       0.0, 1.0,
                xpos + w, ypos,       1.0, 1.0,

                xpos,     ypos - h,   0.0, 0.0,
                xpos + w, ypos,       1.0, 1.0,
                xpos + w, ypos - h,   1.0, 0.0,
            ], dtype=np.float32)

            glBindTexture(GL_TEXTURE_2D, ch.texture)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            glDrawArrays(GL_TRIANGLES, 0, 6)

            start_x += (ch.advance >> 6) * text_surface.scale

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)