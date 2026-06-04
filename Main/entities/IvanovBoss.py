import Dvishok as pygame
import math

class IvanovBoss:
    def __init__(self, screen, battle_ui, ui_scale=1.0):
        self.screen = screen
        self.ui = battle_ui
        self.ui_scale = ui_scale

        self.state = "IDLE"
        self.current_minigame = None
        self.battle_over = False

        self.name = "ИВАНОВ"
        self.max_health = 100
        self.cur_hp = self.max_health

        self.phase = 1

        # --- СИСТЕМА ДИАЛОГОВ ---
        self.current_dialogue = ""
        self.displayed_dialogue = ""
        self.dialogue_queue = []
        self.dialogue_char_index = 0
        self.dialogue_timer = 0
        self.dialogue_speed = 2
        self.dialogue_done = True
        self.dialogue_complete_timer = 0
        self.auto_advance_delay = 150
        self.dialogue_box_rect = None

        self.dialogues = {
            "start": [
                "Слушай внимательно, студент...",
                "Используй WASD для движения!",
                "Уклоняйся от моих атак!",
                "Атакуй, когда будешь готов!"
            ],
            "phase1": [
                "Двигайся! Не стой на месте!",
                "A и D - влево и вправо",
                "W и S - вверх и вниз",
                "Смотри на мои атаки и реагируй!"
            ],
            "phase2": [
                "Вторая фаза! Атаки быстрее!",
                "Используй все клавиши WASD!",
                "Не зажимайся в углу!",
                "Двигайся по всей арене!"
            ],
            "phase3": [
                "ФИНАЛЬНАЯ ФАЗА!",
                "Это твой последний шанс!",
                "Покажи всё, чему научился!",
                "WASD - твои лучшие друзья!"
            ],
            "low_hp": [
                "Я... Не могу... Проиграть...",
                "Ты хорошо двигался...",
                "Используй WASD до конца!"
            ]
        }

        self.cur_pattern = None

        self.patterns = {
            1: ["Cердечный граф"],
            2: ["Cердечный граф"],
            3: ["Cердечный граф"]
        }

        # --- СПРАЙТЫ (Иванова) ---
        self.head_sprite = None
        self.body_sprite = None

        screen_height = screen.get_height()
        screen_width = screen.get_width()

        sprite_width = int(screen_width * 0.25)

        head_aspect_ratio = 728 / 264
        body_aspect_ratio = 728 / 778

        self.head_width = sprite_width
        self.head_height = int(sprite_width / head_aspect_ratio)

        self.body_width = sprite_width
        self.body_height = int(sprite_width / body_aspect_ratio)

        self.head_size = (self.head_width, self.head_height)
        self.body_size = (self.body_width, self.body_height)

        boss_center_x = screen_width // 2 - self.body_size[0] // 2

        head_overlap = int(self.body_height * 0.10)

        self.base_head_y = int(50 * ui_scale)
        self.base_body_y = self.base_head_y + self.head_size[1] - head_overlap

        self.base_head_x = boss_center_x
        self.base_body_x = boss_center_x

        self.time = 0
        self.head_amplitude = int(3.1 * ui_scale)
        self.body_amplitude = int(10 * ui_scale)
        self.head_frequency = 0.03
        self.body_frequency = 0.025

        self.shake_timer = 0
        self.head_phase = 0
        self.body_phase = math.pi / 2
        self.flash_timer = 0

        self.head_rect = pygame.Rect(
            self.base_head_x, self.base_head_y,
            self.head_size[0], self.head_size[1]
        )
        self.body_rect = pygame.Rect(
            self.base_body_x, self.base_body_y,
            self.body_size[0], self.body_size[1]
        )

        self.load_sprites()

    def load_sprites(self):
        """Загрузка спрайтов Иванова"""
        try:
            sprite_paths = [
                "Sprites/Ivanov_head.png",
                "../Sprites/Ivanov_head.png",
                "Assets/Sprites/Ivanov_head.png"
            ]

            for path in sprite_paths:
                try:
                    original = pygame.image.load(path)
                    self.head_sprite = pygame.transform.scale(original, self.head_size)
                    print(f"Голова Иванова загружена: {self.head_size}")
                    break
                except:
                    continue

            for path in sprite_paths:
                try:
                    body_path = path.replace("head", "body")
                    original = pygame.image.load(body_path)
                    self.body_sprite = pygame.transform.scale(original, self.body_size)
                    print(f"Тело Иванова загружено: {self.body_size}")
                    break
                except:
                    continue

        except Exception as e:
            print(f"Ошибка загрузки спрайтов Иванова: {e}")

    def show_dialogue(self, lines):
        self.dialogue_queue = lines.copy()
        self.dialogue_done = False
        self.display_next_dialogue()

    def display_next_dialogue(self):
        if self.dialogue_queue:
            self.current_dialogue = self.dialogue_queue.pop(0)
            self.displayed_dialogue = ""
            self.dialogue_char_index = 0
            self.dialogue_timer = 0
            self.dialogue_complete_timer = 0
            self.dialogue_done = False
        else:
            self.current_dialogue = ""
            self.displayed_dialogue = ""
            self.dialogue_done = True

    def update_dialogue(self):
        if not self.dialogue_done and self.current_dialogue:
            if self.dialogue_char_index < len(self.current_dialogue):
                self.dialogue_timer += 1
                if self.dialogue_timer >= self.dialogue_speed:
                    self.dialogue_timer = 0
                    self.displayed_dialogue += self.current_dialogue[self.dialogue_char_index]
                    self.dialogue_char_index += 1
            else:
                self.dialogue_complete_timer += 1
                if self.dialogue_complete_timer >= self.auto_advance_delay:
                    self.display_next_dialogue()

    def draw_dialogue_box(self, screen):
        if self.displayed_dialogue:
            font = pygame.font.Font(None, int(26 * self.ui_scale))

            box_x = self.body_rect.right + int(15 * self.ui_scale)
            box_y = self.body_rect.centery - int(50 * self.ui_scale)

            text_surface = font.render(self.displayed_dialogue, True, (255, 255, 255))
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()

            padding = int(15 * self.ui_scale)
            box_width = max(text_width + padding * 2, int(180 * self.ui_scale))
            box_height = text_height + padding * 2

            if box_x + box_width > screen.get_width():
                box_x = self.body_rect.left - box_width - int(15 * self.ui_scale)

            if box_y < 0:
                box_y = int(10 * self.ui_scale)

            self.dialogue_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

            pygame.draw.rect(screen, (0, 0, 0), self.dialogue_box_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.dialogue_box_rect, 2)

            text_x = box_x + padding
            text_y = box_y + padding
            screen.blit(text_surface, (text_x, text_y))

    def update_animation(self):
        self.time += 1

        head_offset_x = math.sin(self.time * self.head_frequency + self.head_phase) * self.head_amplitude
        head_offset_y = math.cos(self.time * self.head_frequency * 0.7 + self.head_phase) * (self.head_amplitude // 3)

        body_offset_x = math.sin(self.time * self.body_frequency + self.body_phase) * self.body_amplitude
        body_offset_y = math.cos(self.time * self.body_frequency * 0.8 + self.body_phase) * (self.body_amplitude // 3)

        self.head_rect.x = self.base_head_x + head_offset_x
        self.head_rect.y = self.base_head_y + head_offset_y

        self.body_rect.x = self.base_body_x + body_offset_x
        self.body_rect.y = self.base_body_y + body_offset_y

    def update(self):
        self.update_animation()
        self.update_dialogue()

        # Обновляем мини-игру, но НЕ завершаем её автоматически
        if self.current_minigame:
            self.current_minigame.update()
            # ⚠️ ВАЖНО: убрали автоматический вызов end_attack()
            # if self.current_minigame.is_finished():
            #     self.end_attack()

        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.head_amplitude = int(5 * self.ui_scale)
                self.body_amplitude = int(12 * self.ui_scale)

        if self.flash_timer > 0:
            self.flash_timer -= 1

    def start_attack(self, pattern_name, minigame):
        self.state = "ATTACKING"
        self.current_pattern = pattern_name
        self.current_minigame = minigame
        self.ui.add_message(f"ИВАНОВ использует: {pattern_name}!")

    def end_attack(self):
        self.state = "IDLE"
        self.current_minigame = None
        self.current_pattern = None

    def take_damage(self, amount):
        self.cur_hp = max(0, self.cur_hp - amount)
        self.flash_timer = 10
        self.shake_timer = 20
        self.head_amplitude = int(3.8 * self.ui_scale)
        self.body_amplitude = int(11 * self.ui_scale)

    def draw(self, screen):
        # Тело (сзади)
        if self.body_sprite:
            if self.flash_timer > 0:
                tinted = self.body_sprite.copy()
                tinted.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tinted, self.body_rect)
            else:
                screen.blit(self.body_sprite, self.body_rect)
        else:
            color = (100, 50, 50) if self.flash_timer > 0 else (60, 30, 30)
            pygame.draw.rect(screen, color, self.body_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.body_rect, 2)

        # Голова (спереди)
        if self.head_sprite:
            if self.flash_timer > 0:
                tinted = self.head_sprite.copy()
                tinted.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tinted, self.head_rect)
            else:
                screen.blit(self.head_sprite, self.head_rect)
        else:
            color = (150, 50, 50) if self.flash_timer > 0 else (100, 30, 30)
            pygame.draw.rect(screen, color, self.head_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.head_rect, 2)