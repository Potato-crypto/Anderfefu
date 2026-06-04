from Dvishok.Sprite.Font.TextSurface import TextSurface


class Surface:
    def __init__(self, camera, width, height, x = 0, y = 0):
        self.camera = camera
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def draw(self):
        pass

    def blit(self, obj, x, y):
        """Отображает переданный объект по определенным для него правилам """
        from Dvishok.Sprite.Sprite.SpriteSurface import SpriteSurface
        if isinstance(obj, TextSurface):
            obj.font.draw(
                obj,
                x,
                y,
                self.width,
                self.height
            )
        # if isinstance(obj, ImageSurface):
        #     obj.image.draw(obj, x, y, self.width, self.height)
        if isinstance(obj, SpriteSurface):
            obj.draw()

    def set_color(self, color):
        pass

    def update(self):
        pass

    def set_size(self, width, height):
        self.width = width
        self.height = height