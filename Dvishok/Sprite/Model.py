from pyglm import glm

from Dvishok.Camera import Camera


class Model:
    def __init__(self, camera: Camera, transform: glm.mat4 = None, rotation: glm.mat4 = None, scale: glm.mat4 = None) -> None:
        self.MVP = None
        self.transform = transform if transform is not None else glm.mat4(1.0)
        self.rotation = rotation if rotation is not None else glm.mat4(1.0)
        self.scaling = scale if scale is not None else glm.mat4(1.0)
        self.camera = camera
        self._mvp_dirty = True
        self.buildMVP()

    def _set_dirty(self):
        self._mvp_dirty = True

    def translate_model(self, vector:glm.vec3):
        translation = glm.translate(glm.vec3(vector.x, vector.y, vector.z))
        self.transform = translation * self.transform

        self.buildMVP()
        self._set_dirty()

    def rotate_model(self, axis: glm.vec3, angle_rad: float):
        rot = glm.rotate(angle_rad, axis)
        self.rotation = rot * self.rotation

        self.buildMVP()
        self._set_dirty()

    def rotate_around_point(self, origin:glm.vec3, axis: glm.vec3, angle_rad: float):
        rot = glm.rotate(angle_rad, axis)
        transform_to_origin = glm.translate(glm.vec3(-origin.x, -origin.y, -origin.z))
        transform_back = glm.translate(glm.vec3(origin.x, origin.y, origin.z))

        self.transform = transform_back * rot * transform_to_origin * self.transform

        self.rotation = rot * self.rotation

        self.buildMVP()
        self._set_dirty()

    def scale_model(self, vector:glm.vec3):
        scale = glm.scale(glm.vec3(vector.x, vector.y, 1))
        self.scaling = scale * self.scaling

        self.buildMVP()
        self._set_dirty()

    def getModel(self) -> glm.mat4:
        return self.transform * self.rotation * self.scaling

    def decompose(self):
        scale = glm.vec3()
        orientation = glm.quat()
        translation = glm.vec3()
        skew = glm.vec3()
        perspective = glm.vec4()
        glm.decompose(self.getModel(), scale, orientation, translation, skew, perspective)
        return scale, orientation, translation, skew, perspective

    def buildMVP(self):
        self.MVP = self.camera.getOrthoMatrix() * \
                   self.getModel()
        self._mvp_dirty = False

    def getMVP(self):
        if self._mvp_dirty:
            self.buildMVP()
        return self.MVP

    def get_width(self):
        return self.decompose()[0]

    def get_height(self):
        return self.decompose()[0]