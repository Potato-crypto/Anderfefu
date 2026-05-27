import os  # Добавь этот импорт в начало файла!
from Main.GameLogic.Intro import Intro
from Main.GameLogic.MainMenu import Menu
from Main.GameLogic.PauseMenu import PauseMenu
from Main.Settings.Settings import *
from Main.GameLogic.logic import SplashScreen
from Main.GameLogic.MainGameClasses import TiledMap, Camera, Player


class Game:
    def __init__(self):
        # Инициализация pygame происходит в Settings.py
        # Начальная конфигурация
        self.font = pg.font.Font(MAIN_FONT, 32)
        pg.display.set_caption("UNDERFEFU")
        pg.display.set_icon(MAIN_ICON_IMG)

        # Остальное
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN | pg.SCALED)
        self.full_screen = True
        self.running = True
        self.clock = pg.time.Clock()

        # Интро компании
        self.intro = Intro("company", self.screen)

        # Меню
        self.menu = Menu(self.screen)

        # Пауза
        self.pause = PauseMenu(self.screen)

        # Сюжетное интро
        self.splash = SplashScreen(self.screen)

        # Флаги состояний
        self.company_intro_active = True
        self.splash_intro_active = False
        self.menu_active = False
        self.pause_active = False
        self.game_active = False
        self.splash_shown = False

        # Игровые объекты
        self.game_map = None
        self.player = None
        self.camera = None
        self.project_root = None  # Добавляем project_root как атрибут класса

    def start_game(self):
        """Запуск новой игры"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))

            print(f"DEBUG start_game: script_dir = {script_dir}")
            print(f"DEBUG start_game: project_root = {project_root}")

            # Загружаем первую карту (коридор) - используем corridor.tmx
            map_path = os.path.join(project_root, "map", "location1", "corridor.tmx")
            print(f"DEBUG start_game: map_path = {map_path}")
            print(f"Файл существует: {os.path.exists(map_path)}")

            self.game_map = TiledMap(map_path, scale=4, map_type="corridor")

            # Находим спавн
            spawn_x, spawn_y = self.game_map.find_spawn()
            self.player = Player(spawn_x, spawn_y, self.game_map)

            # Сохраняем корневую директорию для переходов
            self.project_root = project_root
            print(f"DEBUG start_game: self.project_root сохранен = {self.project_root}")

            # Создаем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)

            print("DEBUG start_game: ИГРА УСПЕШНО ЗАГРУЖЕНА")
            return True
        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")
            import traceback
            traceback.print_exc()
            return False

    def change_map(self, new_map_path, map_type, spawn_x=None, spawn_y=None):
        """Смена текущей карты с сохранением направления игрока"""
        try:
            print(f"=== НАЧАЛО ПЕРЕХОДА ===")
            print(f"Путь к новой карте: {new_map_path}")
            print(f"Тип карты: {map_type}")
            print(f"Файл существует: {os.path.exists(new_map_path)}")

            # Сохраняем направление игрока
            saved_direction = self.player.current_direction if self.player else 'down'
            print(f"Сохраненное направление: {saved_direction}")

            # Загружаем новую карту
            self.game_map = TiledMap(new_map_path, scale=4, map_type=map_type)
            print(f"Карта загружена: размер {self.game_map.width}x{self.game_map.height}")

            # Находим спавн - ЕСЛИ НЕ ПЕРЕДАНЫ КООРДИНАТЫ
            if spawn_x is None or spawn_y is None:
                spawn_x, spawn_y = self.game_map.find_spawn()
                print(f"Спавн найден автоматически: ({spawn_x}, {spawn_y})")
            else:
                print(f"Использую заданные координаты спавна: ({spawn_x}, {spawn_y})")

                # ОТЛАДКА: проверяем, какой тайл находится в точке спавна
                tile_x = int(spawn_x // self.game_map.tilewidth)
                tile_y = int(spawn_y // self.game_map.tileheight)
                if 0 <= tile_x < self.game_map.width and 0 <= tile_y < self.game_map.height:
                    gid = self.game_map.layers[0][tile_y][tile_x]
                    print(f"Тайл в точке спавна ({tile_x}, {tile_y}) имеет GID = {gid}")
                    if gid not in [0, 10]:
                        print(f"ПРЕДУПРЕЖДЕНИЕ: Спавн в непроходимом тайле! GID={gid}")

            # Создаем нового игрока
            self.player = Player(spawn_x, spawn_y, self.game_map)
            print(f"Игрок создан на позиции ({self.player.rect.x}, {self.player.rect.y})")
            print(f"Центр игрока: ({self.player.rect.centerx}, {self.player.rect.centery})")

            # Восстанавливаем направление
            self.player.current_direction = saved_direction
            print(f"Направление восстановлено: {self.player.current_direction}")

            # Обновляем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)
            print(f"Камера обновлена")

            print(f"=== ПЕРЕХОД УСПЕШНО ЗАВЕРШЕН ===")
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

            print("ПЕРЕХОД! Игрок коснулся двери!")

            if self.project_root:
                labyrinth_path = os.path.join(self.project_root, "map", "location2", "лабиринт.tmx")

                # Временно загружаем карту, чтобы найти безопасные координаты
                temp_map = TiledMap(labyrinth_path, scale=4, map_type="labyrinth")

                # Ищем безопасное место для спавна в первой допустимой зоне
                # Зона 1: x от 580 до 697, y от 33 до 270
                safe_x = None
                safe_y = None

                for y in range(temp_map.height):
                    for x in range(temp_map.width):
                        world_x = x * temp_map.tilewidth + temp_map.tilewidth // 2
                        world_y = y * temp_map.tileheight + temp_map.tileheight // 2

                        # Проверяем, находится ли точка в зоне 1
                        if 580 <= world_x <= 697 and 33 <= world_y <= 270:
                            # Проверяем, что тайл проходимый
                            gid = temp_map.layers[0][y][x]
                            if gid == 0 or gid == 10:
                                safe_x = world_x
                                safe_y = world_y
                                print(f"Найдено безопасное место для спавна: тайл ({x}, {y}), GID={gid}")
                                print(f"Координаты спавна: ({safe_x}, {safe_y})")
                                break
                    if safe_x is not None:
                        break

                if safe_x is None:
                    # Если не нашли, используем центр зоны 1
                    safe_x = (580 + 697) // 2
                    safe_y = (33 + 270) // 2
                    print(f"Использую центр зоны 1: ({safe_x}, {safe_y})")

                print(f"ВЫЗЫВАЮ change_map с координатами спавна: ({safe_x}, {safe_y})")
                result = self.change_map(labyrinth_path, "labyrinth", safe_x, safe_y)
                print(f"Результат change_map: {result}")
                return True
            else:
                print("ОШИБКА: self.project_root = None!")

        return False

    def update_game(self):
        """Обновление игровой логики"""
        if self.pause_active:
            return

        keys = pg.key.get_pressed()
        if self.player:
            self.player.update(keys)
            self.camera.update(self.player.rect)

            # Проверяем переход через дверь (теперь change_map вызывается внутри check_door_transition)
            self.check_door_transition()

    def draw_game(self):
        """Отрисовка игры"""
        if not self.game_active:
            return

        if self.game_map and self.camera:
            self.game_map.render(self.screen, self.camera)

        if self.player and self.camera:
            self.player.render(self.screen, self.camera)
            # Выводим позицию игрока (можно закомментировать если не нужно)
            font = pg.font.Font(None, 36)
            pos_text = font.render(f"Player: {self.player.rect.x}, {self.player.rect.y}", True, (255, 255, 255))
            self.screen.blit(pos_text, (10, 10))

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
                    print("ЗАПУСКАЕМ ИГРУ!")
                    self.menu_active = False
                    self.game_active = True
                    # Копируем игровые объекты из меню
                    self.game_map = self.menu.game_map
                    self.player = self.menu.player
                    self.camera = self.menu.camera
                    # Сохраняем project_root из меню (ТЕПЕРЬ ЭТО РАБОТАЕТ!)
                    if hasattr(self.menu, 'project_root') and self.menu.project_root:
                        self.project_root = self.menu.project_root
                        print(f"DEBUG: project_root загружен из меню = {self.project_root}")
                    else:
                        print("WARNING: у меню нет атрибута project_root!")
                        # Создаем вручную
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        self.project_root = os.path.dirname(os.path.dirname(script_dir))
                        print(f"DEBUG: project_root создан вручную = {self.project_root}")
                continue

            # Обработка событий паузы (когда она активна)
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
                    # Сбрасываем меню
                    self.menu = Menu(self.screen)
                elif result == "exit":
                    self.running = False
                continue

            # Обработка игровых событий (когда игра активна и пауза не активна)
            if self.game_active and not self.pause_active:
                # Управление паузой
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

            # Если пауза активна, отрисовываем её поверх игры
            if self.pause_active:
                self.pause.draw()

            # ОБНОВЛЯЕМ игровую логику
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
    game.run()