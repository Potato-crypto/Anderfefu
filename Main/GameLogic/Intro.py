from Main.Settings.Settings import *

#Гетеросексуальная заставка для игры
class Intro:
    def __init__(self, intro_type, surface, text="INVALIDY"):
        self.intro_type = intro_type # Название команды, иконка босса и т.д. (нужно будет придумать еще)
        self.font = pg.font.Font(MAIN_FONT, 72) # Шрифт
        self.surface = surface # Поверхность, на которой располагается интро
        self.duration = DURATIONS.get(intro_type) # Длительность интро
        self.text = text # Текст, который будет отображаться
        self.start_time = pg.time.get_ticks() # Старт интро


        # Звук прикольный
        self.sound_effect = pg.mixer.Sound("Main/Sounds/your-best-nightmare.mp3")
        self.sound_played = False

        self.alpha = 0 # Начальная прозрачность текста
        self.fade_speed = 10 # Скорость "появления" текста
        self.direction = 1 # 1 - появляется; -1 - исчезает
        self.active = True # Активность интро

        # Создаем сам текст
        self.title = self.font.render(text, True, "White")
        self.title.set_alpha(self.alpha) # в начале не видно текст

        self.rec_title = self.title.get_rect(center=(SCREEN_WIDTH // 2 , SCREEN_HEIGHT // 2))


    # Появление текста (повышение прозрачности текстовки)
    def update(self):
        cur_time = pg.time.get_ticks()
        cur_duration = cur_time - self.start_time

        self.alpha += self.fade_speed * self.direction

        if not self.sound_played and self.alpha > 0 and self.direction == 1:
            self.sound_effect.play()
            self.sound_played = True

        if self.alpha >= 255:
            self.alpha = 255
            if cur_duration > self.duration - 1000:
                self.direction = -1
        elif self.alpha <= 0:
            self.alpha = 0
            self.active = False
            self.sound_effect.stop()

        self.title.set_alpha(self.alpha)


    # Начальное рисование текста
    def draw(self):
        if self.active:
            self.surface.fill(BACKGROUND_COLOR)
            self.surface.blit(self.title, self.rec_title)


    # Запуск интро
    def run(self):
        if self.active:
            self.draw()
            self.update()
            return True
        return  False
