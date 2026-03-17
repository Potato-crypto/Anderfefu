import pygame
import sys
import os
import random

'''
НИЖЕ КЛАСС ДЛЯ ОТОБРАЖЕНИЯ ЗАСТАВКИ (test_splash.py АКТИВАЦИЯ ЗАСТАВКИ)
'''

class SplashScreen:
    def __init__(self, screen,
                 pages=None,
                 page_durations=None,
                 font_size=None,
                 color=None,
                 bg_color=None,
                 image_paths=None,
                 sound_path=None,
                 line_spacing=None,
                 image_size=None,
                 image_pos=None,
                 text_start_pos=None,
                 font_path=None,
                 typing_sound_path=None,
                 page_font_sizes=None,
                 page_colors=None,
                 page_text_align=None,
                 fade_durations=None,
                 fade_modes=None):

        default_pages = [
            "Однажды две расы правили землёй:\nОТЛИЧНИКИ и ТЕ, КТО ПОПАДАЕТ\nНА КОМИССИЮ.",
            "Так было всегда, и так будет\nвовеки.",
            "Но однажды, в один прекрасный\nсолнечный день, ГРЯНУЛА СЕССИЯ.",
            "Это была долгая и кровопролитная\nвойна. Как между ПРЕПОДАВАТЕЛЯМИ,\nТак и между самими СТУДЕНТАМИ.",
            "Пока одни студенты учили, зубрили\nи корпели над конспектами...",
            "...ДРУГИЕ изворачивались как\nмогли.",
            "",
            "ДВФУ, 2025 г.",
            "Легенды гласят, что те, кто\nпопадают на комиссию...",
            "...Больше не занимаются по\nвечерам, сёрфингом.",
            "",
            "",
            "",
            ""
        ]

        default_page_durations = [5.5, 3, 6, 6, 5, 3, 1, 8, 5, 6, 6, 6, 4, 9]
        default_image_paths = [
            "Anderfefu/texture/SplashScreen/TwoRace.jpg",
            "Anderfefu/texture/SplashScreen/TwoRace.jpg",
            "Anderfefu/texture/SplashScreen/2.jpg",
            "Anderfefu/texture/SplashScreen/3.jpg",
            "Anderfefu/texture/SplashScreen/3.1.jpg",
            None,
            None,
            "Anderfefu/texture/SplashScreen/FEFUT.jpg",
            "Anderfefu/texture/SplashScreen/4.jpg",
            "Anderfefu/texture/SplashScreen/5.jpg",
            "Anderfefu/texture/SplashScreen/6.jpg",
            "Anderfefu/texture/SplashScreen/7.jpg",
            "Anderfefu/texture/SplashScreen/7.1.jpg",
            "Anderfefu/texture/SplashScreen/8.jpg",
        ]
        default_font_size = 17
        default_color = (255, 255, 255)
        default_bg_color = (0, 0, 0)
        default_sound_path = "Anderfefu/soundtrack/Undertale_Soundtrack_-_1_Once_Upon_a_Time_Undertale_OST_70348777.mp3"
        default_line_spacing = 20
        default_image_size = (500, 290)
        default_image_pos = (400, 250)
        default_text_start_pos = (100, 450)
        default_font_path = "Anderfefu/fonts/SMB1NESClassix-Regular.otf"
        default_typing_sound_path = "Anderfefu/soundtrack/SND_TXT2.wav"
        default_page_font_sizes = [17] * 7 + [14] + [17] * 6
        default_page_colors = [
            (255,255,255)] * 7 + [(255,200,100)] + [(255,255,255)] * 6
        default_page_text_align = ["left"] * 7 + ["center"] + ["left"] * 6
        default_fade_durations = [0]*7 + [2.0] + [0]*4 + [0, 8.0]
        default_fade_modes = ["none"]*7 + ["in"] + ["none"]*4 + ["none", "out"]

        self.pages = pages if pages is not None else default_pages
        self.page_durations = page_durations if page_durations is not None else default_page_durations
        self.font_size = font_size if font_size is not None else default_font_size
        self.color = color if color is not None else default_color
        self.bg_color = bg_color if bg_color is not None else default_bg_color
        self.sound_path = sound_path if sound_path is not None else default_sound_path
        self.line_spacing = line_spacing if line_spacing is not None else default_line_spacing
        self.image_size = image_size if image_size is not None else default_image_size
        self.image_pos = image_pos if image_pos is not None else default_image_pos
        self.text_start_pos = text_start_pos if text_start_pos is not None else default_text_start_pos
        self.font_path = font_path if font_path is not None else default_font_path
        self.typing_sound_path = typing_sound_path if typing_sound_path is not None else default_typing_sound_path
        self.image_paths = image_paths if image_paths is not None else default_image_paths
        self.page_font_sizes = page_font_sizes if page_font_sizes is not None else default_page_font_sizes
        self.page_colors = page_colors if page_colors is not None else default_page_colors
        self.page_text_align = page_text_align if page_text_align is not None else default_page_text_align
        self.fade_durations = fade_durations if fade_durations is not None else default_fade_durations
        self.fade_modes = fade_modes if fade_modes is not None else default_fade_modes

        num_pages = len(self.pages)
        self.page_durations = self._fix_list_length(self.page_durations, num_pages, 5.0)
        self.image_paths = self._fix_list_length(self.image_paths, num_pages, None)
        self.page_font_sizes = self._fix_list_length(self.page_font_sizes, num_pages, self.font_size)
        self.page_colors = self._fix_list_length(self.page_colors, num_pages, self.color)
        self.page_text_align = self._fix_list_length(self.page_text_align, num_pages, "left")
        self.fade_durations = self._fix_list_length(self.fade_durations, num_pages, 0.0)
        self.fade_modes = self._fix_list_length(self.fade_modes, num_pages, "none")

        self.screen = screen
        self.current_page = 0

        self.font = self._load_font(self.font_path, self.font_size)

        screen_rect = self.screen.get_rect()
        self.image_center = self.image_pos if self.image_pos else screen_rect.center

        self.page_images = [None] * num_pages
        for i, path in enumerate(self.image_paths):
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if self.image_size:
                    img = pygame.transform.scale(img, self.image_size)
                self.page_images[i] = img

        self.sound = None
        if self.sound_path and os.path.exists(self.sound_path):
            self.sound = pygame.mixer.Sound(self.sound_path)

        self.typing_sound = None
        if self.typing_sound_path and os.path.exists(self.typing_sound_path):
            self.typing_sound = pygame.mixer.Sound(self.typing_sound_path)

        self._load_page(self.current_page)

    def _fix_list_length(self, lst, target_len, default):
        if lst is None:
            return [default] * target_len
        if len(lst) < target_len:
            return lst + [default] * (target_len - len(lst))
        return lst[:target_len]

    def _load_font(self, font_path, font_size):
        if font_path and os.path.exists(font_path):
            return pygame.font.Font(font_path, font_size)
        return pygame.font.Font(None, font_size)

    def _load_page(self, page_index):
        text = self.pages[page_index]
        self.lines = text.split('\n')
        self.char_indices = [0] * len(self.lines)
        self.current_line = 0
        self.char_timer = 0
        self.char_interval = 50
        self.full_text_rendered = False

        if self.page_images[page_index]:
            self.original_image = self.page_images[page_index].copy()
            self.current_image = self.original_image.copy()
        else:
            self.original_image = None
            self.current_image = None

        self.current_page_duration = int(self.page_durations[page_index] * 1000)

        self.current_font_size = self.page_font_sizes[page_index]
        self.current_color = self.page_colors[page_index]
        self.current_text_align = self.page_text_align[page_index]
        self.current_font = self._load_font(self.font_path, self.current_font_size)

        self.fade_duration_ms = int(self.fade_durations[page_index] * 1000)
        self.fade_mode = self.fade_modes[page_index]

        self.fade_start_time = None
        self.fade_direction = None
        self.fade_complete = False

        if self.fade_duration_ms > 0 and self.current_image and self.fade_mode in ["in", "both"]:
            self.current_image.set_alpha(0)
            self.fade_start_time = pygame.time.get_ticks()
            self.fade_direction = "in"

    def _update_fade(self, current_time):
        if self.fade_duration_ms <= 0 or not self.current_image or self.fade_direction is None:
            return False

        if self.fade_start_time is None:
            return False

        elapsed = current_time - self.fade_start_time
        progress = min(elapsed / self.fade_duration_ms, 1.0)

        if self.fade_direction == "in":
            alpha = int(255 * progress)
            self.current_image.set_alpha(alpha)
            if progress >= 1.0:
                self.fade_direction = None
                self.fade_start_time = None
                return True
        elif self.fade_direction == "out":
            alpha = int(255 * (1 - progress))
            self.current_image.set_alpha(alpha)
            if progress >= 1.0:
                self.fade_direction = None
                self.fade_start_time = None
                return True
        return False

    def _start_fade_out(self):
        if self.fade_duration_ms > 0 and self.current_image and self.fade_mode in ["out", "both"]:
            self.fade_direction = "out"
            self.fade_start_time = pygame.time.get_ticks()
            return True
        return False

    def show(self):
        clock = pygame.time.Clock()
        page_start_time = pygame.time.get_ticks()

        transition_scheduled = False
        fading_out = False
        next_page_ready = False
        skip_intro = False

        if self.sound:
            self.sound.play()

        running = True
        while running:
            dt = clock.tick(60)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    skip_intro = True
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass

            if skip_intro:
                running = False
                continue

            if not transition_scheduled and current_time - page_start_time >= self.current_page_duration:
                transition_scheduled = True
                if self._start_fade_out():
                    fading_out = True
                else:
                    next_page_ready = True

            fade_finished = self._update_fade(current_time)
            if fade_finished and fading_out:
                fading_out = False
                next_page_ready = True

            if next_page_ready:
                self._next_page()
                if self.current_page >= len(self.pages):
                    running = False
                else:
                    page_start_time = current_time
                    transition_scheduled = False
                    fading_out = False
                    next_page_ready = False

            if not transition_scheduled and not self.full_text_rendered and not skip_intro:
                self.char_timer += dt
                if self.char_timer >= self.char_interval:
                    self.char_timer = 0
                    if self.char_indices[self.current_line] < len(self.lines[self.current_line]):
                        self.char_indices[self.current_line] += 1
                        if self.typing_sound:
                            self.typing_sound.play()
                    else:
                        if self.current_line < len(self.lines) - 1:
                            self.current_line += 1
                        else:
                            self.full_text_rendered = True

            self.draw()
            pygame.display.flip()

        if self.sound:
            self.sound.stop()

    def _next_page(self):
        self.current_page += 1
        if self.current_page < len(self.pages):
            self._load_page(self.current_page)

    def draw(self):
        self.screen.fill(self.bg_color)

        if self.current_image:
            img_rect = self.current_image.get_rect()
            img_rect.center = self.image_center
            self.screen.blit(self.current_image, img_rect)

        x_base, y = self.text_start_pos
        for i, line in enumerate(self.lines):
            if self.char_indices[i] > 0:
                display_line = line[:self.char_indices[i]]
                surf = self.current_font.render(display_line, True, self.current_color)

                if self.current_text_align == "center":
                    x = (self.screen.get_width() - surf.get_width()) // 2
                else:
                    x = x_base

                self.screen.blit(surf, (x, y))
            y += self.current_font.get_height() + self.line_spacing


'''
НИЖЕ КЛАСС ДЛЯ ИНИЦИАЛИЗАЦИИ БОЯ (test_battle.py АКТИВАЦИЯ БОЯ, ОШИБКИ ВОЗМОЖНО ЕСТЬ Я ХЗ)
'''

class BattleUI:
    ORANGE = (255, 165, 0)

    def __init__(self, screen,
                 main_buttons=None,
                 font_path=None,
                 font_size=10,
                 text_color=(255, 255, 255),
                 button_outline_color=(255, 255, 255),
                 button_bg_color=(0, 0, 0),
                 bg_color=(0, 0, 0),
                 button_width=None,
                 button_height=80,
                 button_spacing=20,
                 text_area_height=150,
                 text_area_bg_color=None,
                 text_area_outline_color=None,
                 text_area_bottom_margin=1,          # изменено с 3 на 1 для соблюдения отступов
                 # Параметры шкалы здоровья
                 max_hp=20,
                 current_hp=20,
                 health_bar_height=15,
                 health_bar_color=(255, 255, 0),
                 health_bar_outline=(255, 255, 255)):

        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.base_button_outline_color = button_outline_color
        self.button_bg_color = button_bg_color
        self.text_color = text_color
        self.bg_color = bg_color

        self.button_height = button_height
        self.button_spacing = button_spacing
        self.text_area_height = text_area_height
        self.text_area_bottom_margin = text_area_bottom_margin

        if text_area_bg_color is None:
            self.text_area_bg_color = bg_color
        else:
            self.text_area_bg_color = text_area_bg_color

        if text_area_outline_color is None:
            self.text_area_outline_color = button_outline_color
        else:
            self.text_area_outline_color = text_area_outline_color

        if font_path and os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.Font(None, font_size)

        self.main_buttons = main_buttons if main_buttons else ["СПИСАТЬ", "ДЕЙСТВИЕ", "ПРЕДМЕТЫ", "ДУМАТЬ"]
        self.main_button_count = len(self.main_buttons)
        self.main_button_outline_colors = [self.base_button_outline_color] * self.main_button_count
        self.main_button_rects = []
        self.hovered_main = -1

        if button_width is None:
            total_spacing = self.button_spacing * (self.main_button_count + 1)
            self.main_button_width = (self.screen_width - total_spacing) // self.main_button_count
        else:
            self.main_button_width = button_width

        start_x = self.button_spacing
        start_y = self.screen_height - self.button_height - self.button_spacing
        for i in range(self.main_button_count):
            rect = pygame.Rect(
                start_x + i * (self.main_button_width + self.button_spacing),
                start_y,
                self.main_button_width,
                self.button_height
            )
            self.main_button_rects.append(rect)

        self.original_main_buttons_y = self.main_button_rects[0].y

        # --- Текстовая область (поднята на 5 пикселей, но с учётом нового bottom_margin) ---
        self.text_area_rect = pygame.Rect(
            self.button_spacing,
            start_y - self.text_area_height - health_bar_height - self.text_area_bottom_margin - 5,
            self.screen_width - 2 * self.button_spacing,
            self.text_area_height
        )

        # --- Параметры здоровья ---
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.health_bar_height = health_bar_height
        self.health_bar_color = health_bar_color
        self.health_bar_outline = health_bar_outline

        # Фиксированная ширина полосы здоровья (не меняется при сужении)
        self.fixed_health_bar_width = self.text_area_rect.width // 5

        self.popup_buttons = []
        self.popup_button_rects = []
        self.popup_button_outline_colors = []
        self.popup_layout = 'horizontal'
        self.hovered_popup = -1

        self.selected_type = 'main'
        self.selected_index = 0
        self.using_keyboard = False

        self.current_messages = []
        self.initial_message = ""
        self.message_history = []
        self.max_messages = 10

        self.input_enabled = True

    # ----- Методы для управления вводом -----
    def enable_input(self):
        self.input_enabled = True

    def disable_input(self):
        self.input_enabled = False

    def set_main_buttons_y(self, y):
        for rect in self.main_button_rects:
            rect.y = y

    # ----- Методы для сообщений -----
    def set_initial_message(self, text):
        self.initial_message = text
        self.current_messages = [text]
        self.message_history = []

    def set_message(self, text):
        self.message_history.append(self.current_messages.copy())
        self.current_messages = [text]

    def add_message(self, text):
        self.message_history.append(self.current_messages.copy())
        self.current_messages.append(text)
        if len(self.current_messages) > self.max_messages:
            self.current_messages.pop(0)

    def restore_initial(self):
        self.current_messages = [self.initial_message]
        self.message_history = []

    def go_back(self):
        if self.message_history:
            self.current_messages = self.message_history.pop()
            return True
        return False

    # ----- Управление здоровьем -----
    def set_hp(self, current, max_hp=None):
        self.current_hp = current
        if max_hp is not None:
            self.max_hp = max_hp
        if self.current_hp < 0:
            self.current_hp = 0
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def set_health_bar_width(self, width):
        """Устанавливает фиксированную ширину полосы здоровья (в пикселях)."""
        self.fixed_health_bar_width = width

    # ----- Всплывающие кнопки -----
    def set_popup_buttons(self, button_texts, outline_colors=None, layout='horizontal', padding=10):
        self.popup_buttons = button_texts
        self.popup_layout = layout
        count = len(button_texts)

        if outline_colors is None:
            self.popup_button_outline_colors = [None] * count
        elif isinstance(outline_colors, (tuple, list)) and len(outline_colors) == count:
            self.popup_button_outline_colors = outline_colors
        else:
            self.popup_button_outline_colors = [outline_colors] * count

        text_surfs = [self.font.render(t, True, self.text_color) for t in button_texts]
        max_width = max(s.get_width() for s in text_surfs)
        max_height = max(s.get_height() for s in text_surfs)
        btn_width = max_width + 2 * padding
        btn_height = max_height + 2 * padding

        area = self.text_area_rect
        self.popup_button_rects = []

        if layout == 'horizontal':
            total_width = count * btn_width + (count - 1) * padding
            start_x = area.x + (area.width - total_width) // 2
            y = area.y + (area.height - btn_height) // 2
            for i in range(count):
                rect = pygame.Rect(
                    start_x + i * (btn_width + padding),
                    y,
                    btn_width,
                    btn_height
                )
                self.popup_button_rects.append(rect)
        else:  # vertical
            total_height = count * btn_height + (count - 1) * padding
            start_y = area.y + (area.height - total_height) // 2
            x = area.x + (area.width - btn_width) // 2
            for i in range(count):
                rect = pygame.Rect(
                    x,
                    start_y + i * (btn_height + padding),
                    btn_width,
                    btn_height
                )
                self.popup_button_rects.append(rect)

        self.selected_type = 'popup'
        self.selected_index = 0
        self.using_keyboard = True

    def clear_popup_buttons(self):
        self.popup_buttons = []
        self.popup_button_rects = []
        self.popup_button_outline_colors = []
        self.hovered_popup = -1
        self.selected_type = 'main'
        self.selected_index = 0
        self.using_keyboard = True

    # ----- Обработка событий -----
    def handle_event(self, event):
        if not self.input_enabled:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return -2
            return -1

        if event.type == pygame.MOUSEMOTION:
            self.hovered_popup = -1
            self.hovered_main = -1
            for i, rect in enumerate(self.popup_button_rects):
                if rect.collidepoint(event.pos):
                    self.hovered_popup = i
                    self.selected_type = 'popup'
                    self.selected_index = i
                    self.using_keyboard = False
                    return -1
            for i, rect in enumerate(self.main_button_rects):
                if rect.collidepoint(event.pos):
                    self.hovered_main = i
                    self.selected_type = 'main'
                    self.selected_index = i
                    self.using_keyboard = False
                    return -1
            return -1

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.popup_button_rects):
                if rect.collidepoint(event.pos):
                    self.selected_type = 'popup'
                    self.selected_index = i
                    self.using_keyboard = False
                    return i + 1000
            for i, rect in enumerate(self.main_button_rects):
                if rect.collidepoint(event.pos):
                    self.selected_type = 'main'
                    self.selected_index = i
                    self.using_keyboard = False
                    return i

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return -2

            if event.key in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
                self.using_keyboard = True
                if self.selected_type == 'main':
                    if event.key == pygame.K_a:
                        self.selected_index = (self.selected_index - 1) % len(self.main_buttons)
                    elif event.key == pygame.K_d:
                        self.selected_index = (self.selected_index + 1) % len(self.main_buttons)
                elif self.selected_type == 'popup' and self.popup_buttons:
                    if self.popup_layout == 'horizontal':
                        if event.key == pygame.K_a:
                            self.selected_index = (self.selected_index - 1) % len(self.popup_buttons)
                        elif event.key == pygame.K_d:
                            self.selected_index = (self.selected_index + 1) % len(self.popup_buttons)
                    else:
                        if event.key == pygame.K_w:
                            self.selected_index = (self.selected_index - 1) % len(self.popup_buttons)
                        elif event.key == pygame.K_s:
                            self.selected_index = (self.selected_index + 1) % len(self.popup_buttons)
                return -1

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_type == 'main' and self.main_buttons:
                    return self.selected_index
                elif self.selected_type == 'popup' and self.popup_buttons:
                    return 1000 + self.selected_index

        return -1

    # ----- Отрисовка шкалы здоровья -----
    def _draw_health_bar(self):
        # Вертикальное положение: через 3 пикселя после нижней границы текстовой области
        bar_y = self.text_area_rect.bottom + 4
        bar_height = self.health_bar_height
        bar_width = self.fixed_health_bar_width

        # Центрирование относительно текущей текстовой области
        bar_x = self.text_area_rect.centerx - bar_width // 2

        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

        # Фон (чёрный)
        pygame.draw.rect(self.screen, self.bg_color, bar_rect)

        # Заливка здоровья с отступами 4 пикселя со всех сторон
        if self.max_hp > 0:
            available_width = bar_width - 8  # слева и справа по 4
            fill_width = int((self.current_hp / self.max_hp) * available_width)
            if fill_width > 0:
                fill_x = bar_x + 4
                fill_y = bar_y + 4
                fill_height = bar_height - 8
                fill_rect = pygame.Rect(fill_x, fill_y, fill_width, fill_height)
                pygame.draw.rect(self.screen, self.health_bar_color, fill_rect)

        # Рамка
        pygame.draw.rect(self.screen, self.health_bar_outline, bar_rect, 2)

        # Текст HP слева от полосы (вертикально по центру)
        hp_text = f"{self.current_hp} HP"
        text_surf = self.font.render(hp_text, True, self.text_color)
        text_x = bar_rect.left - text_surf.get_width() - 10
        text_y = bar_rect.centery - text_surf.get_height() // 2
        if text_x < 0:
            text_x = 5
        self.screen.blit(text_surf, (text_x, text_y))

    # ----- Основная отрисовка -----
    def draw(self):
        self.screen.fill(self.bg_color)

        # Текстовая область
        pygame.draw.rect(self.screen, self.text_area_bg_color, self.text_area_rect)
        pygame.draw.rect(self.screen, self.text_area_outline_color, self.text_area_rect, 2)

        # Текст
        y = self.text_area_rect.y + 10
        for msg in self.current_messages[-self.max_messages:]:
            words = msg.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < self.text_area_rect.width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)
            if not lines:
                lines = [msg]

            for line in lines:
                surf = self.font.render(line, True, self.text_color)
                if y + surf.get_height() <= self.text_area_rect.y + self.text_area_height - 10:
                    self.screen.blit(surf, (self.text_area_rect.x + 10, y))
                    y += surf.get_height() + 2
                else:
                    break
            y += 5

        # Шкала здоровья
        self._draw_health_bar()

        # Всплывающие кнопки
        for i, rect in enumerate(self.popup_button_rects):
            if self.selected_type == 'popup' and i == self.selected_index and self.using_keyboard:
                text_color = self.ORANGE
                outline_color = self.ORANGE if self.popup_button_outline_colors[i] is not None else None
            else:
                text_color = self.text_color
                outline_color = self.popup_button_outline_colors[i]

            pygame.draw.rect(self.screen, self.button_bg_color, rect)
            if outline_color is not None:
                thickness = 4 if (self.selected_type == 'popup' and i == self.selected_index and self.using_keyboard) else 2
                pygame.draw.rect(self.screen, outline_color, rect, thickness)
            text_surf = self.font.render(self.popup_buttons[i], True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

        # Основные кнопки
        for i, rect in enumerate(self.main_button_rects):
            if self.selected_type == 'main' and i == self.selected_index and self.using_keyboard:
                text_color = self.ORANGE
                outline_color = self.ORANGE
            else:
                text_color = self.text_color
                outline_color = self.main_button_outline_colors[i]

            pygame.draw.rect(self.screen, self.button_bg_color, rect)
            thickness = 4 if (self.selected_type == 'main' and i == self.selected_index and self.using_keyboard) else 2
            pygame.draw.rect(self.screen, outline_color, rect, thickness)
            text_surf = self.font.render(self.main_buttons[i], True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

'''
НИЖЕ КЛАСС ДЛЯ САМОГО БОЯ (test_battle.py ВМЕСТЕ С BattleUI, ТРЕБУЮТСЯ ИЗМЕНЕНИЯ)
'''

class BattleMiniGame:
    def __init__(self, battle_ui, arena_rect, duration=10000, enemy_damage=1, damage_interval=1000):
        self.ui = battle_ui
        self.arena = arena_rect.copy()
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        
        # Параметры игрока
        self.player_radius = 15
        self.player_pos = [self.arena.centerx, self.arena.centery]
        self.player_speed = 5
        self.min_x = self.arena.left + self.player_radius
        self.max_x = self.arena.right - self.player_radius
        self.min_y = self.arena.top + self.player_radius
        self.max_y = self.arena.bottom - self.player_radius
        
        # Враг – квадрат
        enemy_size = 30
        self.enemy_rect = pygame.Rect(0, 0, enemy_size, enemy_size)
        self.enemy_rect.center = (self.arena.centerx, self.arena.centery - 50)
        
        # Параметры урона (могут быть изменены извне)
        self.enemy_damage = enemy_damage
        self.damage_interval = damage_interval
        
        # Состояние урона
        self.last_damage_time = 0
        self.was_colliding = False
        
        self.finished = False
        self.victory = False
        
        print(f"=== BattleMiniGame создан: урон {self.enemy_damage} HP / {self.damage_interval} мс ===")
        print(f"Позиция врага: {self.enemy_rect}")
        print(f"Начальное HP: {self.ui.current_hp}")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.finished = True
            self.victory = False
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Проверка победы по времени
        if current_time - self.start_time >= self.duration:
            self.finished = True
            self.victory = True
            print("Время вышло — победа!")
            return
        
        # Движение игрока
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.player_speed
        if keys[pygame.K_s]: dy += self.player_speed
        if keys[pygame.K_a]: dx -= self.player_speed
        if keys[pygame.K_d]: dx += self.player_speed
        
        if dx != 0 or dy != 0:
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy
            self.player_pos[0] = max(self.min_x, min(self.max_x, new_x))
            self.player_pos[1] = max(self.min_y, min(self.max_y, new_y))
        
        # Проверка столкновения
        player_rect = pygame.Rect(
            self.player_pos[0] - self.player_radius,
            self.player_pos[1] - self.player_radius,
            self.player_radius * 2,
            self.player_radius * 2
        )
        
        colliding = player_rect.colliderect(self.enemy_rect)
        
        # Отслеживаем изменение состояния коллизии
        if colliding and not self.was_colliding:
            # Только что вошли в контакт → немедленный урон
            old_hp = self.ui.current_hp
            self.ui.set_hp(max(0, old_hp - self.enemy_damage))
            self.last_damage_time = current_time
            print(f"Первое касание! Урон: {old_hp} -> {self.ui.current_hp}")
            
            if self.ui.current_hp <= 0:
                self.finished = True
                self.victory = False
                print("Игрок погиб!")
        
        elif colliding and self.was_colliding:
            # Продолжаем контакт → проверяем интервал
            if current_time - self.last_damage_time >= self.damage_interval:
                old_hp = self.ui.current_hp
                self.ui.set_hp(max(0, old_hp - self.enemy_damage))
                self.last_damage_time = current_time
                print(f"Периодический урон: {old_hp} -> {self.ui.current_hp}")
                
                if self.ui.current_hp <= 0:
                    self.finished = True
                    self.victory = False
                    print("Игрок погиб!")
        
        # Если нет коллизии, просто обновляем флаг
        self.was_colliding = colliding
    
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), 
                           (int(self.player_pos[0]), int(self.player_pos[1])), 
                           self.player_radius)
        pygame.draw.rect(screen, (0, 255, 0), self.enemy_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.enemy_rect, 2)
        
        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, (self.duration - elapsed) // 1000)
        font = self.ui.font
        time_surf = font.render(f"Осталось: {remaining} с", True, (255,255,255))
        screen.blit(time_surf, (self.arena.x + 10, self.arena.y + 10))
    
    def is_finished(self):
        return self.finished
    
    def is_victory(self):
        return self.victory