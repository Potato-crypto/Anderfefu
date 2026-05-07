import xml.etree.ElementTree as ET
import csv
import os


class TiledMap:
    """Загрузка карты из .tmx с поддержкой масштабирования."""
    def __init__(self, filename, scale=4):
        self.filename = filename
        self.map_dir = os.path.dirname(filename)
        self.tilewidth = 16
        self.tileheight = 16
        self.width = 0
        self.height = 0
        self.layers = []
        self.tilesets = []
        self.scale = scale
        self._parse_map()

    def _parse_map(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()

        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])

        # Тайлсеты
        for ts in root.findall('tileset'):
            firstgid = int(ts.attrib['firstgid'])
            source = ts.attrib['source']
            self.tilesets.append({
                'firstgid': firstgid,
                'source': source,
                'tiles': None,
                'scaled_tiles': None
            })

        # Слои
        for layer in root.findall('layer'):
            data = layer.find('data')
            if data.attrib.get('encoding') == 'csv':
                csv_data = data.text.strip()
                reader = csv.reader(csv_data.splitlines())
                matrix = []
                for row in reader:
                    int_row = [int(x.strip()) for x in row if x.strip()]
                    matrix.append(int_row)
                self.layers.append(matrix)

        self._load_tileset_images()

    def _load_tileset_images(self):
        for ts in self.tilesets:
            # Используем путь относительно файла карты
            source_path = os.path.join(self.map_dir, ts['source'])
            print(f"Загрузка тайлсета: {source_path}")  # Для отладки

            if not os.path.exists(source_path):
                print(f"Файл тайлсета не найден: {source_path}")
                ts['tiles'] = []
                ts['scaled_tiles'] = []
                continue

            ts_tree = ET.parse(source_path)
            ts_root = ts_tree.getroot()

            image_elem = ts_root.find('image')
            if image_elem is None:
                print(f"В тайлсете {source_path} нет изображения")
                ts['tiles'] = []
                ts['scaled_tiles'] = []
                continue

            image_source = image_elem.attrib['source']
            image_path = os.path.join(os.path.dirname(source_path), image_source)

            print(f"Загрузка изображения: {image_path}")  # Для отладки

            try:
                image = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                print(f"Не удалось загрузить {image_path}: {e}")
                image = pygame.Surface((self.tilewidth, self.tileheight))
                image.fill((255, 0, 255))

            tilecount = int(ts_root.attrib.get('tilecount', 1))
            columns = int(ts_root.attrib.get('columns', 1))

            orig_tiles = []
            scaled_tiles = []
            for i in range(tilecount):
                x = (i % columns) * self.tilewidth
                y = (i // columns) * self.tileheight
                try:
                    tile_surface = image.subsurface((x, y, self.tilewidth, self.tileheight))
                except ValueError:
                    tile_surface = pygame.Surface((self.tilewidth, self.tileheight))
                    tile_surface.fill((255, 0, 0))
                orig_tiles.append(tile_surface)
                # Масштабируем
                scaled = pygame.transform.scale(tile_surface,
                                                (self.tilewidth * self.scale,
                                                 self.tileheight * self.scale))
                scaled_tiles.append(scaled)

            ts['tiles'] = orig_tiles
            ts['scaled_tiles'] = scaled_tiles

    def get_tile_surface(self, gid, scaled=False):
        if gid == 0:
            return None
        for ts in self.tilesets:
            firstgid = ts['firstgid']
            tiles = ts['scaled_tiles'] if scaled else ts['tiles']
            if tiles and firstgid <= gid < firstgid + len(tiles):
                return tiles[gid - firstgid]
        return None

    def get_tile_gid(self, x, y, layer=0):
        tx = int(x // self.tilewidth)
        ty = int(y // self.tileheight)
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.layers[layer][ty][tx]
        return None

    def is_walkable(self, rect, layer=0):
        left = rect.left // self.tilewidth
        right = (rect.right - 1) // self.tilewidth
        top = rect.top // self.tileheight
        bottom = (rect.bottom - 1) // self.tileheight

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if tx < 0 or tx >= self.width or ty < 0 or ty >= self.height:
                    return False
                gid = self.layers[layer][ty][tx]
                if gid not in (0, 1):
                    return False
        return True

    def find_spawn(self, layer=0):
        for y in range(self.height):
            for x in range(self.width):
                if self.layers[layer][y][x] == 1:
                    return (x * self.tilewidth + self.tilewidth // 2,
                            y * self.tileheight + self.tileheight // 2)
        return (0, 0)

    def render(self, surface, camera):
        """Отрисовка с учётом камеры и масштаба."""
        cam_x, cam_y = camera.x, camera.y
        scale = camera.scale
        view_w = surface.get_width() / scale
        view_h = surface.get_height() / scale

        start_x = max(0, int(cam_x // self.tilewidth))
        start_y = max(0, int(cam_y // self.tileheight))
        end_x = min(self.width, int((cam_x + view_w) // self.tilewidth + 1))
        end_y = min(self.height, int((cam_y + view_h) // self.tileheight + 1))

        for layer in self.layers:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    gid = layer[y][x]
                    if gid == 0:
                        continue
                    tile = self.get_tile_surface(gid, scaled=True)
                    if tile:
                        world_x = x * self.tilewidth
                        world_y = y * self.tileheight
                        screen_x = (world_x - cam_x) * scale
                        screen_y = (world_y - cam_y) * scale
                        surface.blit(tile, (screen_x, screen_y))


class Camera:
    """Камера с масштабированием, следующая за целью."""
    def __init__(self, screen_width, screen_height, map_width, map_height, scale=4):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.scale = scale
        self.x = 0
        self.y = 0

    def update(self, target_rect):
        target_cx = target_rect.centerx
        target_cy = target_rect.centery

        desired_x = target_cx - (self.screen_width / self.scale) / 2
        desired_y = target_cy - (self.screen_height / self.scale) / 2

        max_x = self.map_width - self.screen_width / self.scale
        max_y = self.map_height - self.screen_height / self.scale
        self.x = max(0, min(desired_x, max_x))
        self.y = max(0, min(desired_y, max_y))

    def apply(self, rect):
        x = (rect.x - self.x) * self.scale
        y = (rect.y - self.y) * self.scale
        w = rect.width * self.scale
        h = rect.height * self.scale
        return pygame.Rect(x, y, w, h)


class Player:
    """Игрок – красный квадрат."""
    def __init__(self, x, y, game_map):
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.speed = 2
        self.map = game_map
        self.color = (255, 0, 0)

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed
        if dx != 0:
            new_rect = self.rect.move(dx, 0)
            if self.map.is_walkable(new_rect):
                self.rect = new_rect
        if dy != 0:
            new_rect = self.rect.move(0, dy)
            if self.map.is_walkable(new_rect):
                self.rect = new_rect

    def render(self, screen, camera):
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, screen_rect)


# MainGameClasses.py (голова заходит на тело, босс чуть меньше)
import pygame
import math
import random


class MalishevBoss:
    def __init__(self, screen, battle_ui, ui_scale=1.0):
        self.screen = screen
        self.ui = battle_ui
        self.ui_scale = ui_scale

        self.state = "IDLE"
        self.current_minigame = None
        self.battle_over = False

        self.name = "МАЛЫШЕВ"
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

        patterns = {
            1: ["Летающие книги", "Экзаменационные листы", "Лазерная указка"],
            2: ["Летающие книги", "Экзаменационные листы", "Лазерная указка", "Стена дедлайна", "Падающие листы"],
            3: ["Летающие книги", "Экзаменационные листы", "Лазерная указка", "Стена дедлайна", "Падающие листы",
                "Контрольная"]
        }

        self.head_sprite = None
        self.body_sprite = None

        screen_height = screen.get_height()
        screen_width = screen.get_width()

        # УМЕНЬШАЕМ босса - ширина 25% экрана (было 30%)
        sprite_width = int(screen_width * 0.25)

        # Соотношения сторон
        head_aspect_ratio = 728 / 264  # 2.7576
        body_aspect_ratio = 728 / 778  # 0.9357

        self.head_width = sprite_width
        self.head_height = int(sprite_width / head_aspect_ratio)

        self.body_width = sprite_width
        self.body_height = int(sprite_width / body_aspect_ratio)

        self.head_size = (self.head_width, self.head_height)
        self.body_size = (self.body_width, self.body_height)

        # Центрируем босса
        boss_center_x = screen_width // 2 - self.body_size[0] // 2

        # ПОЗИЦИИ: голова НАЛОЖЕНА на тело (заходит вниз на 30% тела)
        head_overlap = int(self.body_height * 0.10)

        self.base_head_y = int(50 * ui_scale)
        # Тело начинается ДО того как голова закончилась (наложение)
        self.base_body_y = self.base_head_y + self.head_size[1] - head_overlap

        self.base_head_x = boss_center_x
        self.base_body_x = boss_center_x

        # Анимация
        self.time = 0

        self.base_head_amplitude_default = int(1.7 * ui_scale)  # Базовая амплитуда
        self.base_body_amplitude_default = int(4.3 * ui_scale)
        self.head_amplitude = self.base_head_amplitude_default
        self.body_amplitude = self.base_body_amplitude_default
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
        """Загрузка обрезанных спрайтов"""
        try:
            sprite_paths = [
                "Sprites/Malishev_head.png",
                "../Sprites/Malishev_head.png",
                "Assets/Sprites/Malishev_head.png"
            ]

            for path in sprite_paths:
                try:
                    original = pygame.image.load(path)
                    self.head_sprite = pygame.transform.scale(original, self.head_size)
                    print(f"Голова загружена: {self.head_size}")
                    break
                except:
                    continue

            for path in sprite_paths:
                try:
                    body_path = path.replace("head", "body")
                    original = pygame.image.load(body_path)
                    self.body_sprite = pygame.transform.scale(original, self.body_size)
                    print(f"Тело загружено: {self.body_size}")
                    break
                except:
                    continue

        except Exception as e:
            print(f"Ошибка загрузки спрайтов: {e}")

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

        if self.current_minigame:
            self.current_minigame.update()
            if self.current_minigame.is_finished():
                self.end_attack()

        # Тряска только при активном shake_timer
        if self.shake_timer > 0:
            self.shake_timer -= 1
            # Временная тряска
            self.head_amplitude = self.base_head_amplitude_default * 3
            self.body_amplitude = self.base_body_amplitude_default * 3
            if self.shake_timer == 0:
                # Возвращаем нормальную амплитуду
                self.head_amplitude = self.base_head_amplitude_default
                self.body_amplitude = self.base_body_amplitude_default

        if self.flash_timer > 0:
            self.flash_timer -= 1

    def start_attack(self, pattern_name, minigame):
        self.state = "ATTACKING"
        self.current_pattern = pattern_name
        self.current_minigame = minigame
        self.ui.add_message(f"МАЛЫШЕВ использует: {pattern_name}!")

    def end_attack(self):
        self.state = "IDLE"
        self.current_minigame = None
        self.current_pattern = None

    def take_damage(self, amount):
        self.cur_hp = max(0, self.cur_hp - amount)
        self.flash_timer = 10
        self.shake_timer = 20


    def draw(self, screen):
        # Отрисовка туловища ПЕРВЫМ (сзади)
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

        # Отрисовка головы ПОВЕРХ (спереди, перекрывает тело)
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