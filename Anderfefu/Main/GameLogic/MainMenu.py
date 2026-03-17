from Main.Settings.Settings import *
import random
import math


class Menu:
    def __init__(self, surface, title="UNDERFEFU"):
        self.surface = surface
        self.active = True  # Активность меню
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

        self.delay_timer = 3000  # Таймер для появления заголовка игры
        self.anim_started = False
        self.anim_completed = False

        # Звук крутой
        self.sound_effect = pg.mixer.Sound("../Sounds/ApperanceTitleSound.mp3")
        self.sound_effect_played = False

        # Приколы для items
        self.item_font = pg.font.Font(MAIN_FONT, 48)
        self.items = ["START", "SETTINGS", "EXIT"]
        self.selected = 0

        self.items_alpha = [0, 0, 0]
        self.fade_speed_item = 4

        # звук для items
        self.sound_items_effect = pg.mixer.Sound("../Sounds/PickSound.mp3")

        # Плавное дрожание
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_time = 0
        self.base_speed = 0.1
        self.base_amount = 3
        self.random_variation = 0

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
            self.rect_title.center = (SCREEN_WIDTH // 2, self.start_position)

        if self.anim_completed:
            # Плавное появление пунктов меню
            for i in range(len(self.items_alpha)):
                self.items_alpha[i] += self.fade_speed_item
                if self.items_alpha[i] >= 255:
                    self.items_alpha[i] = 255

            # дрожание
            self.shake_time += self.base_speed

            if random.random() < 0.02:
                self.random_variation = random.uniform(-0.5, 0.5)

            # Комбинируем плавное движение со случайной вариацией
            self.shake_offset_x = (math.sin(self.shake_time) * self.base_amount) + self.random_variation
            self.shake_offset_y = math.cos(self.shake_time * 1.5) * 1.5  # Меньше по вертикали


    # Отрисовка items
    def draw(self):
        if self.active:
            self.surface.fill(BACKGROUND_COLOR)
            self.surface.blit(self.title, self.rect_title)

            if self.anim_completed:
                y_offset = 400
                for i, item in enumerate(self.items):
                    # Определяем цвет
                    if i == self.selected:
                        if i == 2:
                            color = "Red"
                        else:
                            color = "Green"
                    else:
                        color = "White"

                    # Создаем текст
                    text_surface = self.item_font.render(item, True, color)
                    text_surface.set_alpha(self.items_alpha[i])
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))

                    # Применяем плавное дрожание только к выбранному пункту
                    if i == self.selected:
                        text_rect.x += self.shake_offset_x
                        text_rect.y += self.shake_offset_y

                    self.surface.blit(text_surface, text_rect)
                    y_offset += 100

    def handle_event(self, event):
        if not self.active and not self.anim_completed:
            return

        if event.key == pg.K_DOWN:
            self.selected = (self.selected + 1) % len(self.items)
            self.sound_items_effect.play()

        if event.key == pg.K_UP:
            self.selected = (self.selected - 1) % len(self.items)
            self.sound_items_effect.play()

        if event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN:
            if self.selected == 0: # Нажали на кнопку START
                pass

            if self.selected == 1: # Нажали на кнопку SETTINGS
                pass

            if self.selected == 2: # Нажали на кнопку EXIT
                self.active = False
                pg.quit()


    def run(self):
        if self.active:
            self.draw()
            self.update()
            return True
        return False