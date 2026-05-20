import pygame
import random
import math

class HeartGraphGame:
    def __init__(self, battle_ui, arena_rect, duration=30000,
                 enemy_damage=5, red_interval=2000, damage_cooldown=500, num_red_nodes=2):
        self.ui = battle_ui
        self.arena = arena_rect.copy()
        if self.arena.width < 10 or self.arena.height < 10:
            self.arena.width = max(self.arena.width, 300)
            self.arena.height = max(self.arena.height, 200)

        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.red_interval = red_interval
        self.damage_cooldown = damage_cooldown
        self.enemy_damage = enemy_damage
        self.num_red_nodes = num_red_nodes

        self.num_nodes = 10
        self.nodes = []
        self.edges = []
        self._generate_heart_nodes()
        self._build_edges()

        self.current_node = 0
        self.dangerous_nodes = []
        self.last_color_change = pygame.time.get_ticks()
        self.last_damage_time = pygame.time.get_ticks()
        self.finished = False
        self.victory = False

        # Найдём самую нижнюю точку графа (максимальную Y среди узлов)
        self.max_y = max(y for (_, y) in self.nodes) if self.nodes else self.arena.bottom

    def _generate_heart_nodes(self):
        margin = 10
        w = max(1, self.arena.width - 2 * margin)
        h = max(1, self.arena.height - 2 * margin)
        center_x = self.arena.x + self.arena.width // 2
        center_y = self.arena.y + self.arena.height // 2
        scale = min(w / 32, h / 34) * 1.8
        self.nodes = []
        for i in range(self.num_nodes):
            t = 2 * math.pi * i / self.num_nodes
            x_raw = 16 * math.sin(t) ** 3
            y_raw = 13 * math.cos(t) - 5 * math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)
            x = center_x + x_raw * scale
            y = center_y - y_raw * scale
            self.nodes.append((int(x), int(y)))

    def _build_edges(self):
        self.edges = []
        for i in range(self.num_nodes):
            j = (i + 1) % self.num_nodes
            self.edges.append((i, j))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.current_node = (self.current_node - 1) % self.num_nodes
            elif event.key == pygame.K_d:
                self.current_node = (self.current_node + 1) % self.num_nodes
            elif event.key == pygame.K_ESCAPE:
                self.finished = True
                self.victory = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start_time >= self.duration and not self.finished:
            self.finished = True
            self.victory = True
            return

        # Смена красных узлов каждые 2 секунды
        if now - self.last_color_change >= self.red_interval:
            self.dangerous_nodes = random.sample(range(self.num_nodes), self.num_red_nodes)
            self.last_color_change = now

        # Урон каждые 0.5 секунды, если игрок на красном узле
        if (self.current_node in self.dangerous_nodes and
            now - self.last_damage_time >= self.damage_cooldown):
            new_hp = max(0, self.ui.current_hp - self.enemy_damage)
            self.ui.set_hp(new_hp)
            self.last_damage_time = now
            if new_hp <= 0:
                self.finished = True
                self.victory = False
                return

    def draw(self, screen):
        if not self.nodes:
            return

        # Рисуем рёбра
        for i, j in self.edges:
            if i >= len(self.nodes) or j >= len(self.nodes):
                continue
            pygame.draw.line(screen, (100, 100, 100), self.nodes[i], self.nodes[j], 2)

        # Рисуем узлы
        for idx, pos in enumerate(self.nodes):
            if idx in self.dangerous_nodes:
                color = (255, 0, 0)
            elif idx == self.current_node:
                color = (0, 255, 0)
            else:
                color = (200, 200, 200)
            pygame.draw.circle(screen, color, pos, 14)
            pygame.draw.circle(screen, (255, 255, 255), pos, 14, 2)

        # --- Таймер и полоска HP (под графом) ---
        # Располагаем ниже самой нижней точки узлов + отступ
        info_y = self.max_y + 40  # отступ 40 пикселей от самого нижнего узла
        center_x = self.arena.centerx

        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, (self.duration - elapsed) // 1000)

        if self.ui.font:
            # Таймер
            time_text = self.ui.font.render(f"Осталось: {remaining} с", True, (255, 255, 255))
            time_rect = time_text.get_rect(center=(center_x, info_y))
            screen.blit(time_text, time_rect)

            # Полоска HP
            hp_y = info_y + 30
            hp_rect = pygame.Rect(center_x - 150, hp_y, 300, 25)
            pygame.draw.rect(screen, (60, 60, 60), hp_rect)
            hp_percent = self.ui.current_hp / self.ui.max_hp if self.ui.max_hp > 0 else 0
            fill_width = int(hp_rect.width * hp_percent)
            hp_fill = pygame.Rect(hp_rect.x, hp_rect.y, fill_width, hp_rect.height)
            pygame.draw.rect(screen, (255, 255, 0), hp_fill)
            pygame.draw.rect(screen, (255, 255, 255), hp_rect, 2)

            hp_text = self.ui.font.render(f"HP: {self.ui.current_hp}/{self.ui.max_hp}", True, (255, 255, 255))
            hp_text_rect = hp_text.get_rect(center=(center_x, hp_y - 12))
            screen.blit(hp_text, hp_text_rect)

    def is_finished(self):
        return self.finished

    def is_victory(self):
        return self.victory