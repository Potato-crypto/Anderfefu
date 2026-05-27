from Main.Settings.Settings import *
from Main.GameLogic.MainGameClasses import TiledMap, Camera, Player
import random
import math
import os


class Menu:
    def __init__(self, surface, title="UNDERFEFU"):
        self.surface = surface
        self.active = True
        self.font = pg.font.Font(MAIN_FONT, 72)

        # Параметры для анимации
        self.alpha = 0
        self.fade_speed = 2
        self.anim_speed = 4
        self.start_time = pg.time.get_ticks()

        self.title = self.font.render(title, True, "White")
        self.start_position = 50
        self.rect_title = self.title.get_rect(center=(SCREEN_WIDTH // 2, self.start_position))
        self.title.set_alpha(self.alpha)

        self.delay_timer = 3000
        self.anim_started = False
        self.anim_completed = False

        self.sound_effect = pg.mixer.Sound("../Sounds/ApperanceTitleSound.mp3")
        self.sound_effect_played = False

        self.item_font = pg.font.Font(MAIN_FONT, 48)
        self.items = ["START", "SETTINGS", "EXIT"]
        self.selected = 0

        self.items_alpha = [0, 0, 0]
        self.fade_speed_item = 4

        self.sound_items_effect = pg.mixer.Sound("../Sounds/mus_ohyes_1.mp3")
        self.sound_items_effect.set_volume(0.3)

        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_time = 0
        self.base_speed = 0.1
        self.base_amount = 3
        self.random_variation = 0

        # --- Переменные для игрового процесса ---
        self.game_active = False
        self.game_map = None
        self.player = None
        self.camera = None
        self.project_root = None  # ДОБАВЛЯЕМ ЭТОТ АТРИБУТ

    def update(self):
        cur_time = pg.time.get_ticks()
        cur_duration = cur_time - self.start_time

        if cur_duration >= self.delay_timer:
            self.anim_started = True

        if self.anim_started:
            self.alpha += self.fade_speed
            self.start_position += self.anim_speed

            if not self.sound_effect_played and self.alpha > 0:
                self.sound_effect.play()
                self.sound_effect_played = True

            if self.alpha >= 255:
                self.alpha = 255
            if self.start_position >= 225:
                self.anim_speed = 0
                self.anim_completed = True

            self.title.set_alpha(self.alpha)
            self.rect_title.center = (SCREEN_WIDTH // 2, self.start_position)

        if self.anim_completed:
            for i in range(len(self.items_alpha)):
                self.items_alpha[i] += self.fade_speed_item
                if self.items_alpha[i] >= 255:
                    self.items_alpha[i] = 255

            self.shake_time += self.base_speed

            if random.random() < 0.02:
                self.random_variation = random.uniform(-0.5, 0.5)

            self.shake_offset_x = (math.sin(self.shake_time) * self.base_amount) + self.random_variation
            self.shake_offset_y = math.cos(self.shake_time * 1.5) * 1.5

    def draw_menu(self):
        if self.active:
            self.surface.fill(BACKGROUND_COLOR)
            self.surface.blit(self.title, self.rect_title)

            if self.anim_completed:
                y_offset = 400
                for i, item in enumerate(self.items):
                    if i == self.selected:
                        if i == 2:
                            color = "Red"
                        else:
                            color = "Green"
                    else:
                        color = "White"

                    text_surface = self.item_font.render(item, True, color)
                    text_surface.set_alpha(self.items_alpha[i])
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))

                    if i == self.selected:
                        text_rect.x += self.shake_offset_x
                        text_rect.y += self.shake_offset_y

                    self.surface.blit(text_surface, text_rect)
                    y_offset += 100

    def start_game(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))

            # СОХРАНЯЕМ project_root В АТРИБУТ
            self.project_root = project_root
            print(f"DEBUG Menu.start_game: project_root = {self.project_root}")

            # ПРОВЕРЯЕМ КАКИЕ ФАЙЛЫ СУЩЕСТВУЮТ
            location1_path = os.path.join(project_root, "map", "location1")
            print(f"Содержимое папки {location1_path}:")
            if os.path.exists(location1_path):
                for file in os.listdir(location1_path):
                    print(f"  - {file}")

            # Используем правильное имя файла (corridor.tmx вместо testlocation.tmx)
            map_path = os.path.join(project_root, "map", "location1", "corridor.tmx")
            print(f"DEBUG Menu.start_game: map_path = {map_path}")
            print(f"Файл существует: {os.path.exists(map_path)}")

            # Если corridor.tmx не найден, пробуем найти любой .tmx файл
            if not os.path.exists(map_path):
                # Ищем первый попавшийся .tmx файл
                for file in os.listdir(location1_path):
                    if file.endswith('.tmx'):
                        map_path = os.path.join(location1_path, file)
                        print(f"Найден альтернативный файл: {map_path}")
                        break

            # Создаем карту
            self.game_map = TiledMap(map_path, scale=4, map_type="corridor")

            # Находим спавн и создаем игрока
            spawn_x, spawn_y = self.game_map.find_spawn()
            print(f"Спавн найден: ({spawn_x}, {spawn_y})")

            self.player = Player(spawn_x, spawn_y, self.game_map)

            # Создаем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.surface.get_width(), self.surface.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)

            print("Игра успешно загружена!")
            return True

        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_game(self):
        if not self.game_active:
            return

        keys = pg.key.get_pressed()
        self.player.update(keys)
        self.camera.update(self.player.rect)

    def draw_game(self):
        if not self.game_active:
            return

        self.game_map.render(self.surface, self.camera)
        self.player.render(self.surface, self.camera)

    def handle_event(self, event):
        if not self.active and not self.anim_completed:
            return None

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
                self.sound_items_effect.play()

            if event.key == pg.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
                self.sound_items_effect.play()

            if event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN:
                if self.selected == 0:  # START
                    if self.start_game():
                        self.active = False
                        self.game_active = True
                        return "start"
                    else:
                        print("Ошибка: не удалось загрузить игру!")
                        return None

                if self.selected == 1:  # SETTINGS
                    return None

                if self.selected == 2:  # EXIT
                    return "exit"

        return None

    def run(self):
        if self.game_active:
            self.update_game()
            self.draw_game()
            return True
        elif self.active:
            self.draw_menu()
            self.update()
            return True
        return False