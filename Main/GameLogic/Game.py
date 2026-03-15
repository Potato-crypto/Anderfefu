from Main.GameLogic.Intro import Intro
from Main.GameLogic.MainMenu import Menu
from Main.Settings.Settings import *

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

        # Интро
        self.intro = Intro("company", self.screen)
        self.intro_active = True  # Флаг активности интро

        #Меню
        self.menu = Menu(self.screen)
        self.menu_active = False # Флаг активности меню

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

                # Пропуск интро (клавиша пробел)
                if self.intro_active and event.key == pg.K_SPACE:
                    self.intro.active = False
                    self.intro_active = False
                    self.menu_active = True

    def draw(self):
        if self.intro_active:
            # Запускаем интро
            self.intro_active = self.intro.run()
            if not self.intro_active:
                self.menu_active = True

        elif self.menu_active:
            self.menu.run()
        else:
            # Здесь будет отрисовка основной игры
            self.screen.fill(BACKGROUND_COLOR)  # Заливаем фон только когда интро закончилось


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