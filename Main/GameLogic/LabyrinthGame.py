# LabyrinthGame.py
# Мини-игра "Лабиринт знаний" – собери зелёные мишени
# Плавное движение с проверкой коллизий

import pygame as pg
import random
import math


class LabyrinthGame:
    def __init__(self, battle_ui, arena, scroll_count=5, time_limit=40000, wall_damage=1, rounds=None,
                 unsafe_count=None):
        self.battle_ui = battle_ui
        self.arena = arena
        self.scroll_count = scroll_count
        self.time_limit = time_limit
        self.wall_damage = wall_damage

        self.start_time = pg.time.get_ticks()
        self.score = 0
        self.finished = False
        self.victory = False

        # Игровое поле
        self.game_arena = self.arena.inflate(-10, -10)
        self.game_arena.x = self.arena.x + 5
        self.game_arena.y = self.arena.y + 5

        # Размеры лабиринта
        self.cell_size = 25
        self.grid_cols = self.game_arena.width // self.cell_size
        self.grid_rows = self.game_arena.height // self.cell_size
        self.grid_cols = self.grid_cols if self.grid_cols % 2 == 1 else self.grid_cols - 1
        self.grid_rows = self.grid_rows if self.grid_rows % 2 == 1 else self.grid_rows - 1

        # Генерация лабиринта
        self.walls = []
        self.maze = None  # сохраняем массив лабиринта для проверок
        self.scrolls = []
        self._generate_maze()

        # Параметры игрока
        self.player_radius = self.cell_size // 3
        self.player_radius = max(6, min(12, self.player_radius))
        self.player_pos = [self.game_arena.centerx, self.game_arena.centery]
        self.player_speed = 3  # уменьшил скорость для лучшего контроля
        self.target_radius = self.player_radius - 1

        # Безопасная установка стартовой позиции
        self._place_player_safely()

        # Состояние клавиш
        self.keys_pressed = {
            pg.K_w: False,
            pg.K_s: False,
            pg.K_a: False,
            pg.K_d: False
        }

        # Флаг для анимации столкновения
        self.hit_cooldown = 0
        self.HIT_COOLDOWN_MAX = 30  # кадров между ударами о стену

        # Шрифты и цвета
        self.font = pg.font.Font(None, int(self.target_radius * 1.5))
        self.font_info = pg.font.Font(None, int(self.game_arena.height * 0.08))
        self.bg_color = (20, 20, 40)
        self.wall_color = (70, 70, 120)
        self.wall_outline = (120, 120, 170)
        self.player_color = (255, 50, 50)
        self.target_color = (80, 220, 80)
        self.target_outline = (150, 255, 150)

        # Звуки
        self.sound_collect = self._load_sound("../Sounds/collect.wav", 0.5)
        self.sound_wall = self._load_sound("../Sounds/wall_hit.wav", 0.3)
        self.sound_win = self._load_sound("../Sounds/win.wav", 0.7)
        self.sound_lose = self._load_sound("../Sounds/lose.wav", 0.6)

    def _load_sound(self, path, volume):
        try:
            s = pg.mixer.Sound(path)
            s.set_volume(volume)
            return s
        except:
            return None

    def _generate_maze(self):
        """Генерация лабиринта с сохранением массива"""
        self.maze = [[1 for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]

        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = 0
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            neighbours = []
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.grid_cols - 1 and 0 < ny < self.grid_rows - 1 and self.maze[ny][nx] == 1:
                    neighbours.append((nx, ny, dx // 2, dy // 2))

            if neighbours:
                nx, ny, wx, wy = random.choice(neighbours)
                self.maze[ny][nx] = 0
                self.maze[y + wy][x + wx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # Стены
        self.walls = []
        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                if self.maze[y][x] == 1:
                    rect = pg.Rect(
                        self.game_arena.left + x * self.cell_size,
                        self.game_arena.top + y * self.cell_size,
                        self.cell_size, self.cell_size
                    )
                    self.walls.append(rect)

        # Мишени
        free_cells = []
        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                if self.maze[y][x] == 0:
                    if x != start_x or y != start_y:
                        free_cells.append((x, y))

        if len(free_cells) < self.scroll_count:
            self.scroll_count = len(free_cells)

        if free_cells:
            scroll_positions = random.sample(free_cells, min(self.scroll_count, len(free_cells)))
            for x, y in scroll_positions:
                center = (
                    self.game_arena.left + x * self.cell_size + self.cell_size // 2,
                    self.game_arena.top + y * self.cell_size + self.cell_size // 2
                )
                self.scrolls.append({
                    'center': center,
                    'collected': False
                })

    def _is_collision(self, rect):
        """Проверяет, пересекается ли прямоугольник со стенами"""
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def _can_move_to(self, new_rect):
        """Проверяет, можно ли переместиться в новую позицию"""
        # Проверка границ арены
        if (new_rect.left < self.game_arena.left or
            new_rect.right > self.game_arena.right or
            new_rect.top < self.game_arena.top or
            new_rect.bottom > self.game_arena.bottom):
            return False
        # Проверка столкновения со стенами
        return not self._is_collision(new_rect)

    def _place_player_safely(self):
        """Помещает игрока в центр стартовой клетки"""
        start_x = self.game_arena.left + self.cell_size + self.cell_size // 2
        start_y = self.game_arena.top + self.cell_size + self.cell_size // 2
        self.player_pos = [start_x, start_y]

    def _check_wall_collision_and_move(self):
        """Плавное движение с проверкой коллизий – двигаем отдельно по X и Y"""
        new_x = self.player_pos[0]
        new_y = self.player_pos[1]

        # Движение по X
        if self.keys_pressed[pg.K_a]:
            new_x -= self.player_speed
        if self.keys_pressed[pg.K_d]:
            new_x += self.player_speed

        # Проверяем движение по X
        test_rect = pg.Rect(
            new_x - self.player_radius,
            self.player_pos[1] - self.player_radius,
            self.player_radius * 2,
            self.player_radius * 2
        )
        if self._can_move_to(test_rect):
            self.player_pos[0] = new_x
        elif self.hit_cooldown <= 0:
            # Удар о стену (только при движении)
            if (self.keys_pressed[pg.K_a] or self.keys_pressed[pg.K_d]) and self.hit_cooldown <= 0:
                self.hit_cooldown = self.HIT_COOLDOWN_MAX
                new_hp = max(0, self.battle_ui.current_hp - self.wall_damage)
                self.battle_ui.set_hp(new_hp)
                self.battle_ui.add_message(f"Стена! -{self.wall_damage} HP")
                if self.sound_wall:
                    self.sound_wall.play()
                if new_hp <= 0:
                    self.finished = True
                    self.victory = False
                    return

        # Движение по Y
        if self.keys_pressed[pg.K_w]:
            new_y -= self.player_speed
        if self.keys_pressed[pg.K_s]:
            new_y += self.player_speed

        # Проверяем движение по Y
        test_rect = pg.Rect(
            self.player_pos[0] - self.player_radius,
            new_y - self.player_radius,
            self.player_radius * 2,
            self.player_radius * 2
        )
        if self._can_move_to(test_rect):
            self.player_pos[1] = new_y
        elif self.hit_cooldown <= 0:
            if (self.keys_pressed[pg.K_w] or self.keys_pressed[pg.K_s]) and self.hit_cooldown <= 0:
                self.hit_cooldown = self.HIT_COOLDOWN_MAX
                new_hp = max(0, self.battle_ui.current_hp - self.wall_damage)
                self.battle_ui.set_hp(new_hp)
                self.battle_ui.add_message(f"Стена! -{self.wall_damage} HP")
                if self.sound_wall:
                    self.sound_wall.play()
                if new_hp <= 0:
                    self.finished = True
                    self.victory = False
                    return

    def _apply_damage(self, damage_amount):
        new_hp = max(0, self.battle_ui.current_hp - damage_amount)
        self.battle_ui.set_hp(new_hp)
        return new_hp

    def handle_event(self, event):
        if self.finished:
            return
        if event.type == pg.KEYDOWN:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = True
        elif event.type == pg.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False

    def update(self):
        if self.finished:
            return
        now = pg.time.get_ticks()

        # Обновляем кулдаун удара о стену
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # Движение с проверкой коллизий
        self._check_wall_collision_and_move()

        if now - self.start_time > self.time_limit:
            self.finished = True
            self.victory = (self.score >= self.scroll_count)
            if not self.victory and self.sound_lose:
                self.sound_lose.play()
            elif self.victory and self.sound_win:
                self.sound_win.play()
            return

        # Проверка сбора мишеней
        player_rect = pg.Rect(
            self.player_pos[0] - self.player_radius,
            self.player_pos[1] - self.player_radius,
            self.player_radius * 2,
            self.player_radius * 2
        )
        for scroll in self.scrolls[:]:
            if not scroll['collected']:
                scroll_rect = pg.Rect(
                    scroll['center'][0] - self.target_radius,
                    scroll['center'][1] - self.target_radius,
                    self.target_radius * 2,
                    self.target_radius * 2
                )
                if player_rect.colliderect(scroll_rect):
                    scroll['collected'] = True
                    self.score += 1
                    self.battle_ui.add_message(f"Мишень собрана! {self.score}/{self.scroll_count}")
                    if self.sound_collect:
                        self.sound_collect.play()
                    if self.score >= self.scroll_count:
                        self.finished = True
                        self.victory = True
                        if self.sound_win:
                            self.sound_win.play()
                        return

        if self.battle_ui.current_hp <= 0:
            self.finished = True
            self.victory = False
            if self.sound_lose:
                self.sound_lose.play()
            return

    def draw(self, screen):
        pg.draw.rect(screen, self.bg_color, self.arena)
        pg.draw.rect(screen, (100, 100, 150), self.arena, 3)

        pg.draw.rect(screen, (35, 35, 60), self.game_arena)
        pg.draw.rect(screen, (130, 130, 180), self.game_arena, 2)

        for wall in self.walls:
            pg.draw.rect(screen, self.wall_color, wall)
            pg.draw.rect(screen, self.wall_outline, wall, 1)

        for scroll in self.scrolls:
            if not scroll['collected']:
                pg.draw.circle(screen, self.target_color, scroll['center'], self.target_radius)
                pg.draw.circle(screen, self.target_outline, scroll['center'], self.target_radius, 2)
                pg.draw.circle(screen, (0, 0, 0), scroll['center'], self.target_radius // 2)

        pg.draw.circle(screen, self.player_color, self.player_pos, self.player_radius)
        pg.draw.circle(screen, (255, 200, 200), self.player_pos, self.player_radius, 2)

        info_bg = pg.Surface((self.arena.width, 45), pg.SRCALPHA)
        info_bg.fill((0, 0, 0, 180))
        screen.blit(info_bg, (self.arena.left, self.arena.top))

        score_text = self.font_info.render(f"Мишени: {self.score}/{self.scroll_count}", True, (255, 255, 200))
        screen.blit(score_text, (self.arena.left + 10, self.arena.top + 10))

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