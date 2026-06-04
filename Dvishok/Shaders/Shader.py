from OpenGL.GL import *

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = self._create_program(vertex_path, fragment_path)

    def _read_file(self, path):
        with open(path, "r") as f:
            return f.read()

    def _compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise Exception(glGetShaderInfoLog(shader).decode())

        return shader

    def _create_program(self, vertex_path, fragment_path):
        vertex_src = self._read_file(vertex_path)
        fragment_src = self._read_file(fragment_path)

        vertex = self._compile_shader(vertex_src, GL_VERTEX_SHADER)
        fragment = self._compile_shader(fragment_src, GL_FRAGMENT_SHADER)

        program = glCreateProgram()
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        glLinkProgram(program)

        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise Exception(glGetProgramInfoLog(program))

        glDeleteShader(vertex)
        glDeleteShader(fragment)

        return program

    def use(self):
        glUseProgram(self.program)

    # юниформы (пока что на вектора и флоаты)
    def set_vec4(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform4f(loc, *value)

    def set_mat4(self, name, mat):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, mat)