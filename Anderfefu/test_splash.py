import pygame
import sys
from logic import SplashScreen

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.set_num_channels(64)

    screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Заставка")

    splash = SplashScreen(screen)   
    splash.show()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()