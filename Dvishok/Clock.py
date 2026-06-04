import time

class Clock:
    """
    Класс для управления временем в игровом цикле.
    Работает аналогично pygame.time.Clock.
    """

    def __init__(self):
        self._last_tick = None          # время предыдущего вызова tick (секунды)
        self._fps_start = None          # время начала отсчёта FPS
        self._frame_count = 0           # количество кадров для подсчёта FPS
        self._fps = 0.0                 # текущее среднее FPS

    def tick(self, fps=None):
        """
        Ограничивает частоту кадров и возвращает время, прошедшее с предыдущего вызова.

        :param fps: Максимальное количество кадров в секунду (None — без ограничения)
        :return: Время в миллисекундах между последними двумя вызовами tick (float)
        """
        now = time.perf_counter()

        if self._last_tick is not None:
            elapsed = now - self._last_tick          # секунды
            # Ограничение FPS
            if fps is not None and fps > 0:
                target_delay = 1.0 / fps
                if elapsed < target_delay:
                    time.sleep(target_delay - elapsed)
                    now = time.perf_counter()        # обновляем время после сна
                    elapsed = now - self._last_tick
        else:
            elapsed = 0.0

        self._last_tick = now

        # Обновление статистики FPS (раз в секунду)
        if self._fps_start is None:
            self._fps_start = now
            self._frame_count = 1
        else:
            self._frame_count += 1
            time_since_start = now - self._fps_start
            if time_since_start >= 1.0:
                self._fps = self._frame_count / time_since_start
                self._frame_count = 0
                self._fps_start = now

        return elapsed * 1000.0   # возвращаем миллисекунды

    def tick_seconds(self, fps=None):
        """
        Удобный вариант tick(), возвращающий дельту в секундах.

        :param fps: Максимальное количество кадров в секунду (None — без ограничения)
        :return: Время в секундах между последними двумя вызовами (float)
        """
        return self.tick(fps) / 1000.0

    def get_fps(self):
        """
        Возвращает среднее количество кадров в секунду за последнюю секунду.

        :return: FPS (float)
        """
        return self._fps

    def get_time(self):
        """
        Возвращает время в секундах с момента первого вызова tick().
        Если tick() ещё не вызывался, возвращает 0.

        :return: Время в секундах (float)
        """
        if self._last_tick is None:
            return 0.0
        return time.perf_counter() - self._last_tick

    def reset(self):
        """
        Сбрасывает состояние часов (полезно при перезапуске сцены).
        """
        self._last_tick = None
        self._fps_start = None
        self._frame_count = 0
        self._fps = 0.0