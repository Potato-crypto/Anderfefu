# KuinaGame.py
# Мини-игра "WASD-догонялки" – собирай зелёные мишени
# Победа: собрать target_count мишеней
# Поражение: только если HP <= 0
# Время не влияет на победу/поражение

import pygame as pg
import random
import math


class KuinaGame:
    def __init__(self, battle_ui, arena, target_count=10, time_limit=30000, enemy_damage=5, rounds=None,
                 unsafe_count=None):
        self.battle_ui = battle_ui
        self.arena = arena
        self.target_count = target_count
        self.time_limit = time_limit
        self.enemy_damage = enemy_damage
        self.miss_damage = 1

        self.start_time = pg.time.get_ticks()
        self.score = 0
        self.finished = False
        self.victory = False

        # Игровое поле
        self.game_arena = self.arena.inflate(-20, -20)
        self.game_arena.x = self.arena.x + 10
        self.game_arena.y = self.arena.y + 10

        # Параметры игрока
        self.player_radius = min(self.game_arena.width, self.game_arena.height) // 12
        self.player_pos = [self.game_arena.centerx, self.game_arena.centery]
        self.player_speed = 6

        # Состояние клавиш
        self.keys_pressed = {
            pg.K_w: False,
            pg.K_s: False,
            pg.K_a: False,
            pg.K_d: False
        }

        # Параметры мишеней
        self.targets = []
        self.target_radius = min(self.game_arena.width, self.game_arena.height) // 10
        self.target_lifetime = 5000
        self.spawn_interval = 1000
        self.last_spawn_time = self.start_time
        self.max_targets = 4

        # Шрифты и цвета
        self.font = pg.font.Font(None, int(self.target_radius * 1.2))
        self.font_info = pg.font.Font(None, int(self.game_arena.height * 0.08))
        self.bg_color = (20, 20, 40)
        self.player_color = (255, 50, 50)
        self.target_color = (80, 220, 80)
        self.target_outline = (200, 255, 200)

        # Звуки
        self.sound_collect = self._load_sound("../Sounds/collect.wav", 0.5)
        self.sound_miss = self._load_sound("../Sounds/miss.wav", 0.4)
        self.sound_win = self._load_sound("../Sounds/win.wav", 0.7)
        self.sound_lose = self._load_sound("../Sounds/lose.wav", 0.6)

    def _load_sound(self, path, volume):
        try:
            s = pg.mixer.Sound(path)
            s.set_volume(volume)
            return s
        except:
            return None

    def _spawn_target(self):
        if len(self.targets) >= self.max_targets:
            return
        letter = random.choice(['W', 'A', 'S', 'D'])
        margin = self.target_radius + 5
        min_x = self.game_arena.left + margin
        max_x = self.game_arena.right - margin
        min_y = self.game_arena.top + margin
        max_y = self.game_arena.bottom - margin

        if min_x >= max_x or min_y >= max_y:
            return

        x = random.randint(int(min_x), int(max_x))
        y = random.randint(int(min_y), int(max_y))
        self.targets.append({
            'letter': letter,
            'center': (x, y),
            'birth': pg.time.get_ticks()
        })

    def handle_event(self, event):
        if self.finished:
            return
        if event.type == pg.KEYDOWN:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = True
        elif event.type == pg.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False

    def _apply_movement(self):
        new_x = self.player_pos[0]
        new_y = self.player_pos[1]

        if self.keys_pressed[pg.K_w]:
            new_y -= self.player_speed
        if self.keys_pressed[pg.K_s]:
            new_y += self.player_speed
        if self.keys_pressed[pg.K_a]:
            new_x -= self.player_speed
        if self.keys_pressed[pg.K_d]:
            new_x += self.player_speed

        min_x = self.game_arena.left + self.player_radius
        max_x = self.game_arena.right - self.player_radius
        min_y = self.game_arena.top + self.player_radius
        max_y = self.game_arena.bottom - self.player_radius

        self.player_pos[0] = max(min_x, min(max_x, new_x))
        self.player_pos[1] = max(min_y, min(max_y, new_y))

    def _apply_damage(self, damage_amount):
        new_hp = max(0, self.battle_ui.current_hp - damage_amount)
        self.battle_ui.set_hp(new_hp)
        return new_hp

    def update(self):
        if self.finished:
            return
        now = pg.time.get_ticks()

        self._apply_movement()

        # ===== ПРОВЕРКА ПОБЕДЫ (СБОР МИШЕНЕЙ) – САМЫЙ ПРИОРИТЕТ =====
        for t in self.targets[:]:
            dx = self.player_pos[0] - t['center'][0]
            dy = self.player_pos[1] - t['center'][1]
            dist = math.hypot(dx, dy)
            if dist < self.player_radius + self.target_radius:
                self.targets.remove(t)
                self.score += 1
                self.battle_ui.add_message(f"Собрано! {self.score}/{self.target_count}")
                if self.sound_collect:
                    self.sound_collect.play()

                # ПОБЕДА!
                if self.score >= self.target_count:
                    self.finished = True
                    self.victory = True
                    if self.sound_win:
                        self.sound_win.play()
                    return

        # ===== ПРОВЕРКА ПОРАЖЕНИЯ (HP = 0) =====
        if self.battle_ui.current_hp <= 0:
            self.finished = True
            self.victory = False
            if self.sound_lose:
                self.sound_lose.play()
            return

        # ===== ТАЙМЕР ТОЛЬКО ДЛЯ ИНФОРМАЦИИ, НЕ ЗАВЕРШАЕТ ИГРУ =====
        # (оставлен только для отображения, не влияет на победу/поражение)

        # Удаление устаревших мишеней (наносим урон)
        for t in self.targets[:]:
            if now - t['birth'] > self.target_lifetime:
                self.targets.remove(t)
                new_hp = self._apply_damage(self.miss_damage)
                self.battle_ui.add_message(f"Мишень пропала! -{self.miss_damage} HP")
                if self.sound_miss:
                    self.sound_miss.play()
                # Если после урона HP стало 0 – проигрыш
                if new_hp <= 0:
                    self.finished = True
                    self.victory = False
                    if self.sound_lose:
                        self.sound_lose.play()
                    return

        # Спавн новых мишеней
        if now - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = now
            self._spawn_target()

    def draw(self, screen):
        pg.draw.rect(screen, self.bg_color, self.arena)
        pg.draw.rect(screen, (100, 100, 150), self.arena, 3)

        pg.draw.rect(screen, (30, 30, 55), self.game_arena)
        pg.draw.rect(screen, (120, 120, 170), self.game_arena, 2)

        now = pg.time.get_ticks()
        for t in self.targets:
            age = now - t['birth']
            if age > self.target_lifetime * 0.6:
                alpha_factor = 1 - (age - self.target_lifetime * 0.6) / (self.target_lifetime * 0.4)
                intensity = int(80 + 140 * alpha_factor)
                color = (intensity, intensity, 80)
            else:
                color = self.target_color
            pg.draw.circle(screen, color, t['center'], self.target_radius)
            pg.draw.circle(screen, self.target_outline, t['center'], self.target_radius, 3)
            text = self.font.render(t['letter'], True, (0, 0, 0))
            text_rect = text.get_rect(center=t['center'])
            screen.blit(text, text_rect)

        pg.draw.circle(screen, self.player_color, self.player_pos, self.player_radius)
        pg.draw.circle(screen, (255, 200, 200), self.player_pos, self.player_radius, 3)

        info_bg = pg.Surface((self.arena.width, 45), pg.SRCALPHA)
        info_bg.fill((0, 0, 0, 180))
        screen.blit(info_bg, (self.arena.left, self.arena.top))

        score_text = self.font_info.render(f"Счёт: {self.score}/{self.target_count}", True, (255, 255, 200))
        screen.blit(score_text, (self.arena.left + 10, self.arena.top + 10))

        # Время только для информации (не влияет на игру)
        remaining = max(0, (self.time_limit - (pg.time.get_ticks() - self.start_time)) // 1000)
        time_text = self.font_info.render(f"Время: {remaining} с", True, (200, 200, 255))
        screen.blit(time_text, (self.arena.centerx - time_text.get_width() // 2, self.arena.top + 10))

        bar_width = 200
        bar_height = 18
        bar_x = self.arena.right - bar_width - 15
        bar_y = self.arena.top + 12
        pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        hp_percent = self.battle_ui.current_hp / self.battle_ui.max_hp if self.battle_ui.max_hp > 0 else 0
        fill_width = int(bar_width * hp_percent)
        pg.draw.rect(screen, (255, 255, 0), (bar_x, bar_y, fill_width, bar_height))
        pg.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        hp_text = self.font_info.render(f"HP: {self.battle_ui.current_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (bar_x + 5, bar_y - 14))

        if self.finished:
            overlay = pg.Surface(self.arena.size, pg.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, self.arena)
            msg = "ПОБЕДА!" if self.victory else "ПОРАЖЕНИЕ"
            color = (100, 255, 100) if self.victory else (255, 100, 100)
            end_text = pg.font.Font(None, int(self.arena.height * 0.15)).render(msg, True, color)
            end_rect = end_text.get_rect(center=self.arena.center)
            screen.blit(end_text, end_rect)

    def is_finished(self):
        return self.finished

    def is_victory(self):
        return self.victory