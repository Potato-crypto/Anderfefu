from Main.Settings.Settings import *

class Menu:
    def __init__(self, surface, title = "UNDERFEFU"):
        self.surface = surface
        self.active = True # Активность меню
        self.font = pg.font.Font(MAIN_FONT, 72)

        # Параметры для анимации выдвигающегося текста с названием игры
        self.alpha = 0
        self.fade_speed = 2
        self.anim_speed = 4
        self.start_time = pg.time.get_ticks()

        # Прицепляем шрифт к заголовку игры
        self.title = self.font.render(title, True, "White")
        self.start_position = 50
        self.rect_title = self.title.get_rect(center=(SCREEN_WIDTH // 2, self.start_position))
        self.title.set_alpha(self.alpha)

        self.delay_timer = 3000 # Таймер для появления заголовка игры
        self.anim_started = False
        self.anim_completed = False

        # Звук крутой
        self.sound_effect = pg.mixer.Sound("../Sounds/ApperanceTitleSound.mp3")
        self.sound_effect_played = False

        # Приколы для items
        self.item_font = pg.font.Font(MAIN_FONT, 48)
        self.items = ["START", "SETTINGS", "EXIT"]
        self.selected = 0

        if self.selected == 2:
            self.selected_color = "Red"
        else:
            self.selected_color = "Green"

        self.items_alpha =  [0, 0, 0]
        self.fade_speed_item = 4

    # Анимация всякая
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
            self.rect_title.center = (SCREEN_WIDTH//2, self.start_position)

        if self.anim_completed:
            for i in range(len(self.items_alpha)):
                self.items_alpha[i] += self.fade_speed_item
                if self.items_alpha[i] >= 255:
                    self.items_alpha[i] = 255


    def handle_event(self):
        pass


    # Отрисовка items
    def draw(self):
        if self.active:
            self.surface.fill(BACKGROUND_COLOR)
            self.surface.blit(self.title, self.rect_title)

            if self.anim_completed:
                y_offset = 400
                for i, item in enumerate(self.items):
                    if i == self.selected:
                        color = self.selected_color
                    else:
                        color = "White"

                    text_surface = self.item_font.render(item, True, color)
                    text_surface.set_alpha(self.items_alpha[i])
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))

                    self.surface.blit(text_surface, text_rect)
                    y_offset += 100


    def run(self):
        if self.active:
            self.draw()
            self.update()
            return True
        return False