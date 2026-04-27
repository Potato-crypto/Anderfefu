from Main.Settings.Settings import *
from Main.GameLogic.MainGameClasses import TiledMap, Camera, Player
import random
import math
import os


class PauseMenu:
    def __init__(self, surface, pause_text="PAUSE"):
        self.surface = surface
        self.active = False  # Активно ли меню паузы
        self.font = pg.font.Font(MAIN_FONT, 72)
        self.pause_text = self.font.render(pause_text, True, "White")
        self.rect_pause_text = self.pause_text.get_rect(center=(SCREEN_WIDTH // 2, 224))

        # Дрожание
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_time = 0
        self.base_speed = 0.1
        self.base_amount = 3
        self.random_variation = 0

        # Пункты меню
        self.item_font = pg.font.Font(MAIN_FONT, 48)
        self.items = ["CONTINUE", "SETTINGS", "MAIN MENU", "EXIT"]
        self.selected = 0

        # Звук для навигации
        try:
            self.sound_items_effect = pg.mixer.Sound("../Sounds/PickSound.mp3")
            self.sound_items_effect.set_volume(0.3)
        except:
            self.sound_items_effect = None

    def activate(self):
        """Активировать меню паузы"""
        self.active = True
        self.selected = 0  # Сбрасываем выбор

    def deactivate(self):
        """Деактивировать меню паузы"""
        self.active = False

    def handle_events(self, event):
        """Обработка событий для меню паузы"""
        if not self.active:
            return None

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
                if self.sound_items_effect:
                    self.sound_items_effect.play()

            elif event.key == pg.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
                if self.sound_items_effect:
                    self.sound_items_effect.play()

            elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                if self.selected == 0:  # CONTINUE
                    return "resume"
                elif self.selected == 1:  # SETTINGS
                    # Здесь будет логика настроек
                    return "settings"
                elif self.selected == 2:  # MAIN MENU
                    return "menu"
                elif self.selected == 3:  # EXIT
                    return "exit"

            elif event.key == pg.K_ESCAPE:  # ESC тоже закрывает паузу
                return "resume"

        return None

    def update(self):
        """Обновление эффектов меню паузы"""
        if not self.active:
            return

        # Дрожание для выбранного пункта
        self.shake_time += self.base_speed

        if random.random() < 0.02:
            self.random_variation = random.uniform(-0.5, 0.5)

        self.shake_offset_x = (math.sin(self.shake_time) * self.base_amount) + self.random_variation
        self.shake_offset_y = math.cos(self.shake_time * 1.5) * 1.5

    def draw(self):
        """Отрисовка меню паузы"""
        if not self.active:
            return

        # Полупрозрачный фон
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.surface.blit(overlay, (0, 0))

        # Заголовок PAUSE
        self.surface.blit(self.pause_text, self.rect_pause_text)

        # Пункты меню
        y_offset = 400
        for i, item in enumerate(self.items):
            # Определяем цвет
            if i == self.selected:
                if i == 3:  # EXIT
                    color = "Red"
                else:
                    color = "Green"
            else:
                color = "White"

            # Создаем текст
            text_surface = self.item_font.render(item, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))

            # Применяем дрожание только к выбранному пункту
            if i == self.selected:
                self.update()  # Обновляем дрожание
                text_rect.x += self.shake_offset_x
                text_rect.y += self.shake_offset_y

            self.surface.blit(text_surface, text_rect)
            y_offset += 80  # Уменьшил отступ для 4 пунктов

    def run(self):
        """Запуск меню паузы"""
        if self.active:
            self.draw()
            self.update()
            return True
        return False