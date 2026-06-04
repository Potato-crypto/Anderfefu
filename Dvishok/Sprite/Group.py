from Dvishok.Sprite.Sprite.Surface import Surface
from Dvishok.Sprite.Sprite.SpriteSurface import SpriteSurface


class Group:
    def __init__(self, *obj):
        self.sprites = [o for o in obj]

    def update(self, *args):
        if not args:
            for sprite in self.sprites:
                sprite.update()
        else:
            for sprite in self.sprites:
                sprite.update(*args)

    def draw(self, screen):
        for sprite in self.sprites:
            screen.blit(sprite, sprite.x, sprite.y)

    def get_by_id(self, obj_id):
        return self.sprites[obj_id]

    def get(self):
        return self.sprites

    def add(self, *obj):
        for sprite in obj:
            if isinstance(sprite, SpriteSurface):
                self.sprites.append(sprite)
            else:
                pass

    def pop(self, element):
        if isinstance(element, int):
            self.sprites.pop(element)
            return True
        if isinstance(element, Surface):
            self.sprites.remove(element)
            return True
        return False