import os
import math
from Main.GameLogic.Intro import Intro
from Main.GameLogic.MainMenu import Menu
from Main.GameLogic.PauseMenu import PauseMenu
from Main.Settings.Settings import *
from Main.GameLogic.logic import SplashScreen
from Main.GameLogic.MainGameClasses import TiledMap, Camera, Player
from Main.GameLogic.Malishev_battle import run_boss_battle


class Game:
    def __init__(self):
        # Инициализация pygame происходит в Settings.py
        # Начальная конфигурация
        self.font = pg.font.Font(MAIN_FONT, 32)
        pg.display.set_caption("UNDERFEFU")
        pg.display.set_icon(MAIN_ICON_IMG)

        # # Остальное
        # self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN | pg.SCALED)
        # self.full_screen = True
        # self.running = True
        # self.clock = pg.time.Clock()
        #
        # # Интро компании
        # self.intro = Intro("company", self.screen)
        #
        # # Меню
        # self.menu = Menu(self.screen)
        #
        # # Пауза
        # self.pause = PauseMenu(self.screen)
        #
        # # Сюжетное интро
        # self.splash = SplashScreen(self.screen)
        #
        # # Флаги состояний
        # self.company_intro_active = True
        # self.splash_intro_active = False
        # self.menu_active = False
        # self.pause_active = False
        # self.game_active = False
        # self.splash_shown = False
        #
        # # Игровые объекты
        # self.game_map = None
        # self.player = None
        # self.camera = None
        # self.project_root = None
        #
        # # Флаги для босса
        # self.boss_active = False
        # self.boss_defeated = False
        # self.boss_trigger_zone = (532, 649, 896, 920)
        # self.boss_spawn_position = None

    def start_game(self):
        """Запуск новой игры"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))

            # Загружаем первую карту (коридор)
            map_path = os.path.join(project_root, "map", "location1", "corridor.tmx")

            self.game_map = TiledMap(map_path, scale=4, map_type="corridor")

            # Находим спавн
            spawn_x, spawn_y = self.game_map.find_spawn()
            self.player = Player(spawn_x, spawn_y, self.game_map)

            # Сохраняем корневую директорию для переходов
            self.project_root = project_root

            # Создаем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)

            # Сбрасываем флаги босса при новой игре
            self.boss_defeated = False
            self.boss_active = False

            return True
        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")
            import traceback
            traceback.print_exc()
            return False

    def change_map(self, new_map_path, map_type, spawn_x=None, spawn_y=None):
        """Смена текущей карты с сохранением направления игрока"""
        try:
            # Сохраняем направление игрока
            saved_direction = self.player.current_direction if self.player else 'down'

            # Загружаем новую карту
            self.game_map = TiledMap(new_map_path, scale=4, map_type=map_type)

            # Находим спавн
            if spawn_x is None or spawn_y is None:
                spawn_x, spawn_y = self.game_map.find_spawn()

            # Создаем нового игрока
            self.player = Player(spawn_x, spawn_y, self.game_map)

            # Восстанавливаем направление
            self.player.current_direction = saved_direction

            # Обновляем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)

            return True
        except Exception as e:
            print(f"ОШИБКА при загрузке карты: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_door_transition(self):
        """Проверяет переход через дверь в коридоре"""
        if not self.player or not self.game_map:
            return False

        if self.game_map.map_type != "corridor":
            return False

        door_left = 477
        door_right = 516
        door_top = 73
        door_bottom = 89

        player_center_x = self.player.rect.centerx
        player_center_y = self.player.rect.centery

        if (door_left <= player_center_x <= door_right and
                door_top <= player_center_y <= door_bottom):

            if self.project_root:
                labyrinth_path = os.path.join(self.project_root, "map", "location2", "лабиринт.tmx")
                spawn_x = 631
                spawn_y = 56
                self.change_map(labyrinth_path, "labyrinth", spawn_x, spawn_y)
                return True

        return False

    def start_boss_battle(self):
        """Запускает битву с боссом"""
        # Сохраняем позицию игрока для возврата (с отступом вверх)
        offset_up = 50
        self.boss_spawn_position = (self.player.rect.centerx, self.player.rect.centery - offset_up)

        # Запускаем босс-файт
        victory = run_boss_battle(self.screen)

        if victory:
            # При победе - удаляем триггер (босс побежден)
            self.boss_defeated = True
            print("БОСС ПОБЕЖДЕН! Триггер удален.")
        else:
            # При поражении - оставляем триггер активным
            self.boss_defeated = False
            print("ПОРАЖЕНИЕ! Триггер остался активным.")

        # Возвращаем игрока на сохраненную позицию (с отступом)
        self.player.rect.centerx = self.boss_spawn_position[0]
        self.player.rect.centery = self.boss_spawn_position[1]

        # Обновляем камеру
        self.camera.update(self.player.rect)

        self.boss_active = False

    def check_boss_trigger(self):
        """Проверяет, находится ли игрок в зоне триггера босса"""
        # Если босс побежден - триггер не работает
        if self.boss_defeated:
            return False

        if not self.player or not self.game_map:
            return False

        if self.game_map.map_type != "labyrinth":
            return False

        x1, x2, y1, y2 = self.boss_trigger_zone
        trigger_left = min(x1, x2)
        trigger_right = max(x1, x2)
        trigger_top = min(y1, y2)
        trigger_bottom = max(y1, y2)

        player_center_x = self.player.rect.centerx
        player_center_y = self.player.rect.centery

        if (trigger_left <= player_center_x <= trigger_right and
                trigger_top <= player_center_y <= trigger_bottom):
            return True

        return False

    def draw_arrow_to_target(self, target_center):
        """Рисует стрелку-указатель от игрока к цели (только треугольник)"""
        if not self.player or not self.camera:
            return

        # Получаем центр игрока в мировых координатах
        player_center = (self.player.rect.centerx, self.player.rect.centery)
        target = (target_center[0], target_center[1])

        # Вычисляем направление к цели
        dx = target[0] - player_center[0]
        dy = target[1] - player_center[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 50:  # Если цель близко - не рисуем стрелку
            return

        # Нормализуем направление
        if distance > 0:
            dx = dx / distance
            dy = dy / distance

        # Позиция стрелки - на расстоянии 35 пикселей от центра игрока
        arrow_distance = 35
        arrow_x = player_center[0] + dx * arrow_distance
        arrow_y = player_center[1] + dy * arrow_distance

        # Конвертируем в экранные координаты
        arrow_screen = self.camera.apply(pg.Rect(arrow_x - 4, arrow_y - 4, 8, 8))
        arrow_center = (arrow_screen.centerx, arrow_screen.centery)

        # Вычисляем угол стрелки (в градусах)
        angle = math.degrees(math.atan2(-dy, dx))

        # Рисуем только треугольник (указатель)
        arrow_size = 15
        points = []

        # Острие стрелки (смотрит в направлении цели)
        tip_x = arrow_center[0] + dx * arrow_size
        tip_y = arrow_center[1] + dy * arrow_size

        # Левое и правое крылья стрелки
        perp_dx = -dy  # Перпендикулярное направление
        perp_dy = dx

        wing_size = 7
        left_x = tip_x - dx * (wing_size * 0.7) + perp_dx * wing_size
        left_y = tip_y - dy * (wing_size * 0.7) + perp_dy * wing_size
        right_x = tip_x - dx * (wing_size * 0.7) - perp_dx * wing_size
        right_y = tip_y - dy * (wing_size * 0.7) - perp_dy * wing_size

        points = [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]

        # Добавляем пульсацию (изменение размера и цвета)
        pulse = (math.sin(pg.time.get_ticks() * 0.008) + 1) / 2
        color_intensity = int(150 + pulse * 105)  # От 150 до 255
        color = (color_intensity, 50, 0)  # Оранжевый с пульсацией

        # Рисуем треугольник
        pg.draw.polygon(self.screen, color, points)

        # Добавляем обводку для лучшей видимости
        pg.draw.polygon(self.screen, (255, 100, 0), points, 2)

    def get_trigger_center(self):
        """Возвращает центр активной зоны триггера"""
        if self.boss_defeated:
            return None

        x1, x2, y1, y2 = self.boss_trigger_zone
        center_x = (min(x1, x2) + max(x1, x2)) // 2
        center_y = (min(y1, y2) + max(y1, y2)) // 2
        return (center_x, center_y)

    def draw_boss_trigger(self):
        """Отрисовка зоны триггера босса для визуальной ориентации"""
        if not self.game_active or not self.game_map:
            return

        # Показываем триггер только если босс еще не побежден
        if self.boss_defeated:
            return

        if self.game_map.map_type != "labyrinth":
            return

        x1, x2, y1, y2 = self.boss_trigger_zone
        trigger_left = min(x1, x2)
        trigger_right = max(x1, x2)
        trigger_top = min(y1, y2)
        trigger_bottom = max(y1, y2)

        # Получаем screen координаты зоны
        trigger_world_rect = pg.Rect(trigger_left, trigger_top,
                                     trigger_right - trigger_left,
                                     trigger_bottom - trigger_top)
        screen_rect = self.camera.apply(trigger_world_rect)

        # Рисуем полупрозрачную красную зону
        debug_surface = pg.Surface((screen_rect.width, screen_rect.height), pg.SRCALPHA)
        debug_surface.fill((255, 0, 0, 80))
        self.screen.blit(debug_surface, (screen_rect.x, screen_rect.y))

        # Рисуем мигающую границу
        frame = pg.time.get_ticks() // 200
        if frame % 2 == 0:
            pg.draw.rect(self.screen, (255, 0, 0), screen_rect, 3)
        else:
            pg.draw.rect(self.screen, (255, 100, 0), screen_rect, 3)

        # Рисуем текст "БОСС" над зоной
        font = pg.font.Font(None, 24)
        text = font.render("БОСС", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen_rect.centerx, screen_rect.top - 15))
        self.screen.blit(text, text_rect)

        # Рисуем иконку черепа в центре зоны
        skull_font = pg.font.Font(None, 32)
        skull = skull_font.render("💀", True, (255, 0, 0))
        skull_rect = skull.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        self.screen.blit(skull, skull_rect)

    def update_game(self):
        """Обновление игровой логики"""
        if self.pause_active:
            return

        keys = pg.key.get_pressed()
        if self.player:
            self.player.update(keys)
            self.camera.update(self.player.rect)

            # Проверяем переход через дверь в коридоре
            self.check_door_transition()

            # Проверяем триггер босса
            if not self.boss_active and self.check_boss_trigger():
                self.boss_active = True
                self.start_boss_battle()

    def draw_game(self):
        """Отрисовка игры"""
        if not self.game_active:
            return

        if self.game_map and self.camera:
            self.game_map.render(self.screen, self.camera)

        if self.player and self.camera:
            self.player.render(self.screen, self.camera)

            # Отрисовываем зону триггера босса
            self.draw_boss_trigger()

            # Отрисовываем стрелку-указатель на зону триггера
            trigger_center = self.get_trigger_center()
            if trigger_center and not self.boss_defeated and self.game_map.map_type == "labyrinth":
                self.draw_arrow_to_target(trigger_center)

    def update(self):
        pg.display.update()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F12:
                    if self.full_screen:
                        self.screen = pg.display.set_mode(WINDOW_SIZE)
                        self.full_screen = False
                    else:
                        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
                        self.full_screen = True

                if self.company_intro_active and event.key == pg.K_SPACE:
                    self.company_intro_active = False
                    self.splash_intro_active = True

            # Обработка событий меню
            if self.menu_active:
                result = self.menu.handle_event(event)

                if result == "start":
                    self.menu_active = False
                    self.game_active = True
                    self.game_map = self.menu.game_map
                    self.player = self.menu.player
                    self.camera = self.menu.camera

                    if hasattr(self.menu, 'project_root') and self.menu.project_root:
                        self.project_root = self.menu.project_root
                    else:
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        self.project_root = os.path.dirname(os.path.dirname(script_dir))

                    # Сбрасываем флаги босса при старте новой игры
                    self.boss_defeated = False
                    self.boss_active = False
                continue

            # Обработка событий паузы
            if self.pause_active:
                result = self.pause.handle_events(event)
                if result == "resume":
                    self.pause_active = False
                    self.pause.deactivate()
                elif result == "menu":
                    self.pause_active = False
                    self.pause.deactivate()
                    self.game_active = False
                    self.menu_active = True
                    self.menu = Menu(self.screen)
                elif result == "exit":
                    self.running = False
                continue

            # Обработка игровых событий
            if self.game_active and not self.pause_active:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_active = True
                    self.pause.activate()

    def draw(self):
        # Показываем интро команды
        if self.company_intro_active:
            self.company_intro_active = self.intro.run()
            if not self.company_intro_active:
                self.splash_intro_active = True
            return

        # Показываем сюжетное интро
        if self.splash_intro_active and not self.splash_shown:
            self.splash.show()
            self.splash_shown = True
            self.menu_active = True
            self.splash_intro_active = False
            return

        # Показываем меню
        if self.menu_active:
            self.menu.run()
            return

        # Показываем игру
        if self.game_active:
            self.draw_game()

            if self.pause_active:
                self.pause.draw()

            self.update_game()
            return

        # Если ничего не активно, показываем черный экран
        self.screen.fill(BACKGROUND_COLOR)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.update()
            self.clock.tick(FPS)

        pg.quit()


if __name__ == "__main__":
    game = Game()
    # game.run()