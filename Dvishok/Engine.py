import glfw
from Dvishok.Display import Display
from Dvishok.Events.EventType import EventType
from Dvishok.Events.Event import Event
from Dvishok.Sprite.Audio import AudioEngine

class Engine:
    _SPECIAL_KEYS = {
        glfw.KEY_SPACE: "SPACE",
        glfw.KEY_LEFT_SHIFT: "LEFT SHIFT",
        glfw.KEY_RIGHT_SHIFT: "RIGHT SHIFT",
        glfw.KEY_LEFT_CONTROL: "LEFT CONTROL",
        glfw.KEY_RIGHT_CONTROL: "RIGHT CONTROL",
        glfw.KEY_LEFT_ALT: "LEFT ALT",
        glfw.KEY_RIGHT_ALT: "RIGHT ALT",
        glfw.KEY_TAB: "TAB",
        glfw.KEY_ENTER: "ENTER",
        glfw.KEY_ESCAPE: "ESCAPE",
        glfw.KEY_BACKSPACE: "BACKSPACE",
        glfw.KEY_DELETE: "DELETE",
        glfw.KEY_INSERT: "INSERT",
        glfw.KEY_HOME: "HOME",
        glfw.KEY_END: "END",
        glfw.KEY_PAGE_UP: "PAGE UP",
        glfw.KEY_PAGE_DOWN: "PAGE DOWN",
        glfw.KEY_UP: "UP",
        glfw.KEY_DOWN: "DOWN",
        glfw.KEY_LEFT: "LEFT",
        glfw.KEY_RIGHT: "RIGHT",
        glfw.KEY_CAPS_LOCK: "CAPS LOCK",
        glfw.KEY_NUM_LOCK: "NUM LOCK",
        glfw.KEY_SCROLL_LOCK: "SCROLL LOCK",
        glfw.KEY_PRINT_SCREEN: "PRINT SCREEN",
        glfw.KEY_PAUSE: "PAUSE",
        glfw.KEY_KP_0: "NUM 0",
        glfw.KEY_KP_1: "NUM 1",
        # ... добавить нужные (можно циклом для цифр и букв не надо, они работают)
    }

    def __init__(self):
        self.display = Display()
        self.running = True
        self._pressed_keys = set()
        self.events = []
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.mouse_delta_x = 0.0
        self.mouse_delta_y = 0.0
        self.mouse_locked = False
        self.mouse_buttons = [False, False, False]
        # AudioEngine.init()

    def key_callback(self, window, key, scancode, action, mods):
        name = glfw.get_key_name(key, scancode)
        if name is None:
            name = self._SPECIAL_KEYS.get(key)
            if name is None:
                name = f"UNKNOWN_{key}"

        if action == glfw.PRESS:
            event = Event(EventType.KEYDOWN, window=window, mods=mods, name=name, key=key, scancode=scancode)
            self.events.append(event)
            self._pressed_keys.add(name)
        elif action == glfw.RELEASE:
            event = Event(EventType.KEYUP, window=window, mods=mods, name=name, key=key, scancode=scancode)
            self.events.append(event)
            self._pressed_keys.discard(name)

    def setup_key_callback(self):
        glfw.set_key_callback(self.display.window, self.key_callback)

    def set_mouse_locked(self, locked):
        """Включить/выключить захват мыши (режим FPS)"""
        self.mouse_locked = locked
        mode = glfw.CURSOR_DISABLED if locked else glfw.CURSOR_NORMAL
        glfw.set_input_mode(self.display.window, glfw.CURSOR, mode)

    def cursor_callback(self, window, x, y):
        if self.mouse_locked:
            dx, dy = x, y
            pos = None
        else:
            dx = x - self.mouse_x
            dy = y - self.mouse_y
            pos = (x, y)
            self.mouse_x = x
            self.mouse_y = y

        if dx == 0.0 and dy == 0.0:
            return

        event = Event(EventType.MOUSEMOTION, pos=pos, rel=(dx, dy), buttons=self.mouse_buttons)
        self.events.append(event)

    def setup_mouse_callback(self):
        glfw.set_cursor_pos_callback(self.display.window, self.cursor_callback)
        glfw.set_mouse_button_callback(self.display.window, self.mouse_button_callback)

    def mouse_button_callback(self, window, button, action, mods):

        if action == glfw.PRESS:
            event = Event(EventType.MOUSEBUTTONDOWN, window=window, mods=mods, pos=(self.mouse_x, self.mouse_y), button=button)
            self.mouse_buttons[button] = True
        elif action == glfw.RELEASE:
            event = Event(EventType.MOUSEBUTTONUP, window=window, mods=mods, pos=(self.mouse_x, self.mouse_y), button=button)
            self.mouse_buttons[button] = False
        self.events.append(event)

    def setup_callback(self):
        self.setup_key_callback()
        self.setup_mouse_callback()

    def process_input(self):
        return list(self._pressed_keys)

    def get_events(self):
        return self.events

    def update(self):
        self.events = []
        glfw.swap_buffers(self.display.window)
        glfw.poll_events()
        if glfw.window_should_close(self.display.window):
            self.running = False

    def get_display(self):
        return self.display

    def stop(self):
        self.running = False

    def quit(self):
        glfw.terminate()