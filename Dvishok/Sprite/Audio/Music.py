from Dvishok.Sprite.Audio.Sound import Sound

class Music:

    current = None

    @staticmethod
    def load(path: str):
        Music.current = Sound(path)

    @staticmethod
    def play(loops=-1):
        if Music.current:
            Music.current.play(loops=loops)

    @staticmethod
    def stop():
        if Music.current:
            Music.current.stop()

    @staticmethod
    def pause():
        if Music.current:
            Music.current.pause()

    @staticmethod
    def unpause():
        if Music.current:
            Music.current.unpause()

    @staticmethod
    def fadeout(time_ms=1000):
        if Music.current:
            Music.current.fadeout(time_ms)

    @staticmethod
    def set_volume(volume: float):
        if Music.current:
            Music.current.set_volume(volume)

    @staticmethod
    def get_volume():
        if Music.current:
            return Music.current.get_volume()

        return 0.0