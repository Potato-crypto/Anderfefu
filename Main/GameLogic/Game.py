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
        self.company_intro_active = True  # Интро компании активно
        self.splash_intro_active = False  # Сюжетное интро не активно
        self.menu_active = False  # Меню не активно
        self.pause_active = False  # Пауза не активна
        self.game_active = False  # Добавляем флаг, активна ли игра

        # Флаг для предотвращения повторного запуска сюжетного интро
        self.splash_shown = False

        # Игровые объекты
        self.game_map = None
        self.player = None
        self.camera = None

    def start_game(self):
        """Запуск новой игры"""
        try:
            import os
            # Формируем путь к карте
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            map_path = os.path.join(project_root, "map", "location1", "testlocation.tmx")

            # Создаем карту
            self.game_map = TiledMap(map_path, scale=4)

            # Находим спавн и создаем игрока
            spawn_x = (self.game_map.width // 2) * self.game_map.tilewidth
            spawn_y = (self.game_map.height // 2) * self.game_map.tileheight
            #spawn_x, spawn_y = self.game_map.find_spawn()
            self.player = Player(spawn_x, spawn_y, self.game_map)

            # Создаем камеру
            map_pixel_width = self.game_map.width * self.game_map.tilewidth
            map_pixel_height = self.game_map.height * self.game_map.tileheight
            self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
                                 map_pixel_width, map_pixel_height, scale=4)
            return True
        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")
            return False

    def update_game(self):
        """Обновление игровой логики"""
        if self.pause_active:
            return

        keys = pg.key.get_pressed()
        if self.player:
            self.player.update(keys)
            self.camera.update(self.player.rect)

    def draw_game(self):
        """Отрисовка игры"""
        if not self.game_active:
            return

        if self.game_map and self.camera:
            self.game_map.render(self.screen, self.camera)

        if self.player and self.camera:
            self.player.render(self.screen, self.camera)

            # ОТЛАДКА: рисуем крестик в центре экрана
            screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pg.draw.circle(self.screen, (255, 255, 0), screen_center, 10, 2)
            pg.draw.line(self.screen, (255, 255, 0),
                         (screen_center[0] - 20, screen_center[1]),
                         (screen_center[0] + 20, screen_center[1]), 2)
            pg.draw.line(self.screen, (255, 255, 0),
                         (screen_center[0], screen_center[1] - 20),
                         (screen_center[0], screen_center[1] + 20), 2)

            # Выводим позицию игрока
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
                print(f"Результат из меню: {result}")  # ОТЛАДКА

                if result == "start":
                    print("ЗАПУСКАЕМ ИГРУ!")
                    self.menu_active = False
                    self.game_active = True
                    # Копируем игровые объекты из меню
                    self.game_map = self.menu.game_map
                    self.player = self.menu.player
                    self.camera = self.menu.camera
                    print(f"Объекты скопированы: map={self.game_map}, player={self.player}")
                elif result == "exit":
                    self.running = False
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
                continue  # Не обрабатываем другие события, если пауза активна

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
            self.menu.run()  # Это просто отрисовывает меню
            return

        # Показываем игру
        if self.game_active:
            # ОТРИСОВЫВАЕМ игру
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