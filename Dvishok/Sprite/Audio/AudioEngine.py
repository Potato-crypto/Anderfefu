import sounddevice as sd

class AudioEngine:
    initialized = False
    master_volume = 1.0

    @staticmethod
    def init():
        if not AudioEngine.initialized:
            AudioEngine.initialized = True

    @staticmethod
    def set_volume(volume: float):
        AudioEngine.master_volume = max(0.0, min(1.0, volume))

    @staticmethod
    def get_volume():
        return AudioEngine.master_volume

    @staticmethod
    def stop_all():
        sd.stop()