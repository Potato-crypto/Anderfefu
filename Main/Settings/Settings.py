import pygame as pg
pg.init()

# Иконка главная
MAIN_ICON_IMG = pg.image.load("Main/Images/MainIcon.png")

FPS = 60
# Размер экрана пользователя, для реализации полноэкранного режима
SCREEN_WIDTH = pg.display.Info().current_w
SCREEN_HEIGHT = pg.display.Info().current_h

# Размер окна при оконном режиме
WINDOW_SIZE = (1080, 600)

# Decorate
BACKGROUND_COLOR = "Black"
TEXT_COLOR = "White"
MAIN_FONT = "Main/Fonts/PublicPixel-rv0pA.ttf"

# Для заставки (тип заставки: ее длительность)
DURATIONS = \
{
    "company": 7000,
    "boss_1": 10000,
    "bose_2": 8000
}

