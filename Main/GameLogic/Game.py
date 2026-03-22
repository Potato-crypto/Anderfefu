from Main.GameLogic.Intro import Intro
from Main.GameLogic.MainMenu import Menu
from Main.Settings.Settings import *
from logic import SplashScreen

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
        # Сюжетное интро
        self.splash = SplashScreen(self.screen)

        # Флаги состояний
        self.company_intro_active = True  # Интро компании активно
        self.splash_intro_active = False  # Сюжетное интро не активно
        self.menu_active = False  # Меню не активно

        # Флаг для предотвращения повторного запуска сюжетного интро
        self.splash_shown = False

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

                # Пропуск интро компании (клавиша пробел)
                if self.company_intro_active and event.key == pg.K_SPACE:
                    self.company_intro_active = False
                    self.splash_intro_active = True

                # Обработка событий меню только когда меню активно
                if self.menu_active:
                    self.menu.handle_event(event)

    def draw(self):
        # Показываем интро команды
        if self.company_intro_active:
            self.company_intro_active = self.intro.run()
            if not self.company_intro_active:
                # Интро компании закончилось, запускаем сюжетное интро
                self.splash_intro_active = True

        # Показываем сюжетное интро
        elif self.splash_intro_active and not self.splash_shown:
            self.splash.show()
            self.splash_shown = True
            # После показа сюжетного интро активируем меню
            self.menu_active = True
            self.splash_intro_active = False

        # Показываем меню
        elif self.menu_active:
            self.menu.run()

        # Основная игра (пока пусто)
        else:
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