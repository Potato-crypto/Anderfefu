import threading
import librosa
import sounddevice as sd
from Dvishok.Sprite.Audio.AudioEngine import AudioEngine

class Sound:

    def __init__(self, path: str):

        self.path = path

        self.data, self.sample_rate = librosa.load(
            path,
            sr=None,
            mono=False
        )

        if len(self.data.shape) > 1:
            self.data = self.data.T

        self.volume = 1.0

        self._playing = False
        self._paused = False

        self._thread = None

    def play(self, loops=0):

        if self._playing:
            self.stop()

        self._playing = True
        self._paused = False

        def _playback():

            current_loop = 0

            while self._playing:

                if self._paused:
                    continue

                audio = (
                        self.data
                        * self.volume
                        * AudioEngine.master_volume
                )

                sd.play(audio, self.sample_rate)
                sd.wait()

                if loops == -1:
                    continue

                current_loop += 1

                if current_loop > loops:
                    break

            self._playing = False

        self._thread = threading.Thread(
            target=_playback,
            daemon=True
        )

        self._thread.start()

    def stop(self):

        self._playing = False
        sd.stop()

    def pause(self):

        self._paused = True
        sd.stop()

    def unpause(self):

        self._paused = False

    def fadeout(self, time_ms=1000):

        steps = 20
        delay = time_ms / steps / 1000

        original = self.volume

        for i in range(steps):

            self.volume = original * (
                    1.0 - (i + 1) / steps
            )

            sd.sleep(int(delay * 1000))

        self.stop()

        self.volume = original

    def set_volume(self, volume):

        self.volume = max(
            0.0,
            min(1.0, volume)
        )

    def get_volume(self):

        return self.volume

    def get_length(self):

        return len(self.data) / self.sample_rate

    def is_playing(self):

        return self._playing