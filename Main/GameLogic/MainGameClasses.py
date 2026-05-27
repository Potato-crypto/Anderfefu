import xml.etree.ElementTree as ET
import csv
import os
import pygame as pg
import math


class TiledMap:
    """Загрузка карты из .tmx с поддержкой масштабирования."""

    def __init__(self, filename, scale=4, map_type="corridor"):
        self.filename = filename
        self.map_dir = os.path.dirname(filename)
        self.tilewidth = 16
        self.tileheight = 16
        self.width = 0
        self.height = 0
        self.layers = []
        self.tilesets = []
        self.scale = scale
        self.map_type = map_type  # "corridor" или "labyrinth"
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
            print(f"Загрузка тайлсета: {source_path}")

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

            print(f"Загрузка изображения: {image_path}")

            # ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ФАЙЛА ИЗОБРАЖЕНИЯ
            if not os.path.exists(image_path):
                print(f"ПРЕДУПРЕЖДЕНИЕ: Файл изображения не найден: {image_path}")
                print(f"Создаю заглушку для отсутствующего тайлсета")

                # Создаем заглушку - Surface с прозрачным фоном
                tilecount = int(ts_root.attrib.get('tilecount', 1))
                columns = int(ts_root.attrib.get('columns', 1))

                orig_tiles = []
                scaled_tiles = []

                for i in range(tilecount):
                    # Создаем фиолетовую заглушку для отсутствующих тайлов
                    tile_surface = pg.Surface((self.tilewidth, self.tileheight))
                    tile_surface.fill((255, 0, 255))  # Ярко-розовый/фиолетовый для отладки
                    # Добавляем рамку
                    pg.draw.rect(tile_surface, (255, 255, 255), (0, 0, self.tilewidth, self.tileheight), 1)

                    orig_tiles.append(tile_surface)
                    scaled = pg.transform.scale(tile_surface,
                                                (self.tilewidth * self.scale,
                                                 self.tileheight * self.scale))
                    scaled_tiles.append(scaled)

                ts['tiles'] = orig_tiles
                ts['scaled_tiles'] = scaled_tiles
                print(f"Создана заглушка для {tilecount} тайлов")
                continue

            try:
                image = pg.image.load(image_path).convert_alpha()
            except pg.error as e:
                print(f"Не удалось загрузить {image_path}: {e}")
                image = pg.Surface((self.tilewidth, self.tileheight))
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
                    tile_surface = pg.Surface((self.tilewidth, self.tileheight))
                    tile_surface.fill((255, 0, 0))

                current_gid = ts['firstgid'] + i
                if current_gid == 15 and self.map_type == "corridor":
                    print(f"  Замена двери GID 15 на коричневый цвет")
                    tile_surface = pg.Surface((self.tilewidth, self.tileheight))
                    tile_surface.fill((139, 69, 19))
                    pg.draw.rect(tile_surface, (101, 67, 33), (0, 0, self.tilewidth, self.tileheight), 2)

                orig_tiles.append(tile_surface)
                scaled = pg.transform.scale(tile_surface,
                                            (self.tilewidth * self.scale,
                                             self.tileheight * self.scale))
                scaled_tiles.append(scaled)

            ts['tiles'] = orig_tiles
            ts['scaled_tiles'] = scaled_tiles

            print(f"Загружено {len(orig_tiles)} тайлов, firstgid={ts['firstgid']}")

    def get_tile_surface(self, gid, scaled=False):
        if gid == 0:
            return None
        for ts in self.tilesets:
            firstgid = ts['firstgid']
            tiles = ts['scaled_tiles'] if scaled else ts['tiles']
            if tiles and firstgid <= gid < firstgid + len(tiles):
                return tiles[gid - firstgid]
        return None

    def is_walkable(self, rect):
        """Проверка коллизий в зависимости от типа карты"""
        if self.map_type == "corridor":
            return self._is_walkable_corridor(rect)
        else:
            return self._is_walkable_labyrinth(rect)

    def _is_walkable_corridor(self, rect):
        """Коллизии для коридора - прямоугольная область"""
        min_x = 425
        max_x = 536
        min_y = 80
        max_y = 872

        left = rect.left
        right = rect.right
        top = rect.top
        bottom = rect.bottom

        if (left >= min_x and right <= max_x and
                top >= min_y and bottom <= max_y):
            return True
        return False

    def _is_walkable_labyrinth(self, rect):
        """Коллизии для лабиринта - только в заданных прямоугольных областях"""
        # Получаем центр игрока
        px = rect.centerx
        py = rect.centery

        # ДОПУСТИМЫЕ ОБЛАСТИ (прямоугольники, где можно ходить)
        walkable_zones = [
            (580, 33, 697, 270),  # Зона 1
            (538, 276, 757, 741),  # Зона 2
            (409, 459, 478, 753),  # Зона 3
            (16, 639, 397, 702),  # Зона 4
            (73, 48, 127, 720),  # Зона 5
            (526, 735, 643, 948),  # Зона 6
            (784, 582, 1267, 648),  # Зона 7
            (724, 321, 931, 366),  # Зона 8
            (841, 111, 931, 366),  # Зона 9
            (928, 138, 1273, 210),  # Зона 10
            (582, 260, 687, 1200),  # Зона 11 - БОЛЬШОЙ ЗАЛ (добавлена новая зона)
            (350, 698, 800, 587)
        ]

        # Проверяем, находится ли игрок в любой из допустимых зон
        for x1, y1, x2, y2 in walkable_zones:
            # Нормализуем координаты (чтобы x1 <= x2 и y1 <= y2)
            min_x = min(x1, x2)
            max_x = max(x1, x2)
            min_y = min(y1, y2)
            max_y = max(y1, y2)

            if min_x <= px <= max_x and min_y <= py <= max_y:
                return True

        # Если не в допустимой зоне - ходить нельзя
        return False

    def find_spawn(self, layer=0):
        # Ищем тайл с GID=1 или 10
        for y in range(self.height):
            for x in range(self.width):
                gid = self.layers[layer][y][x]
                if gid == 1 or gid == 10:
                    print(f"Спавн найден на позиции ({x}, {y}) с GID={gid}")
                    return (x * self.tilewidth + self.tilewidth // 2,
                            y * self.tileheight + self.tileheight // 2)

        # Если не нашли, используем центр карты
        center_x = (self.width // 2) * self.tilewidth + self.tilewidth // 2
        center_y = (self.height // 2) * self.tileheight + self.tileheight // 2
        print(f"Тайл спавна не найден, использую центр карты: ({center_x}, {center_y})")
        return (center_x, center_y)

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

        # Отрисовка основного слоя
        for layer in self.layers:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    gid = layer[y][x]
                    if gid == 0:
                        continue

                    if gid == 15 and self.map_type == "corridor":
                        continue

                    tile = self.get_tile_surface(gid, scaled=True)
                    if tile:
                        world_x = x * self.tilewidth
                        world_y = y * self.tileheight
                        screen_x = (world_x - cam_x) * scale
                        screen_y = (world_y - cam_y) * scale
                        surface.blit(tile, (screen_x, screen_y))

        # Рисуем дверь только для коридора
        if self.map_type == "corridor":
            self._render_door(surface, camera)

    def _render_door(self, surface, camera):
        """Отрисовка двери на карте коридора"""
        cam_x, cam_y = camera.x, camera.y
        scale = camera.scale

        door_x = 30
        door_y = 2
        door_width = 2
        door_height = 3

        for dy in range(door_height):
            for dx in range(door_width):
                world_x = (door_x + dx) * self.tilewidth
                world_y = (door_y + dy) * self.tileheight
                screen_x = (world_x - cam_x) * scale
                screen_y = (world_y - cam_y) * scale

                door_tile = pg.Surface((self.tilewidth * scale, self.tileheight * scale))
                door_tile.fill((139, 69, 19))
                pg.draw.rect(door_tile, (101, 67, 33), (0, 0, door_tile.get_width(), door_tile.get_height()), 2)

                if dx == 1 and dy == 1:
                    pg.draw.circle(door_tile, (255, 215, 0),
                                   (door_tile.get_width() - 8, door_tile.get_height() // 2), 4)

                surface.blit(door_tile, (screen_x, screen_y))

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
        return pg.Rect(x, y, w, h)


class Player:
    """Игрок с анимацией движения в 4 направлениях."""

    def __init__(self, x, y, game_map):
        # ВИЗУАЛЬНЫЙ размер (то, что мы видим на экране)
        self.visual_size = 96
        self.hitbox_size = 16

        # Хитбокс (для физики и коллизий)
        self.rect = pg.Rect(x - self.hitbox_size // 2, y - self.hitbox_size // 2,
                            self.hitbox_size, self.hitbox_size)

        self.speed = 3
        self.map = game_map

        # Получаем корневую директорию проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))

        # Загрузка спрайтов
        self.sprites = self._load_sprites()

        # Анимация
        self.current_direction = 'down'
        self.current_frame = 0
        self.animation_speed = 0.25  # Увеличил для замедления анимации (было 0.15)
        self.animation_timer = 0
        self.is_moving = False

        self.color = (255, 0, 0)

    def _load_sprites(self):
        """Загружает все спрайты игрока"""
        sprites = {
            'down': {},
            'up': {},
            'left': {},
            'right': {}
        }

        # Загружаем спрайты для направления ВНИЗ (3 кадра: step1 -> standing -> step2)
        down_standing = self._load_sprite('standing_down.png')
        down_walk1 = self._load_sprite('walk_down_step_1.png')
        down_walk2 = self._load_sprite('walk_down_step_2.png')

        if down_standing:
            sprites['down']['standing'] = down_standing
            # Создаем последовательность кадров для анимации
            if down_walk1 and down_walk2:
                sprites['down']['walk_frames'] = [down_walk1, down_standing, down_walk2]
            elif down_walk1:
                sprites['down']['walk_frames'] = [down_walk1, down_standing, down_walk1]
            else:
                sprites['down']['walk_frames'] = [down_standing]

        # Загружаем спрайты для направления ВВЕРХ (3 кадра: step1 -> standing -> step2)
        up_standing = self._load_sprite('standing_up.png')
        up_walk1 = self._load_sprite('walk_up_step_1.png')
        up_walk2 = self._load_sprite('walk_up_step_2.png')

        if up_standing:
            sprites['up']['standing'] = up_standing
            if up_walk1 and up_walk2:
                sprites['up']['walk_frames'] = [up_walk1, up_standing, up_walk2]
            elif up_walk1:
                sprites['up']['walk_frames'] = [up_walk1, up_standing, up_walk1]
            else:
                sprites['up']['walk_frames'] = [up_standing]

        # Загружаем спрайты для направления ВЛЕВО (3 кадра: walk1 -> walk2 -> standing)
        left_standing = self._load_sprite('standing_left.png')
        left_walk1 = self._load_sprite('walk_left_1.png')
        left_walk2 = self._load_sprite('walk_left_1_2.png')

        if left_standing:
            sprites['left']['standing'] = left_standing
            if left_walk1 and left_walk2:
                sprites['left']['walk_frames'] = [left_walk1, left_walk2, left_standing]
            elif left_walk1:
                sprites['left']['walk_frames'] = [left_walk1, left_standing, left_walk1]
            else:
                sprites['left']['walk_frames'] = [left_standing]

        # Для направления ВПРАВО - зеркально отражаем левые спрайты
        if 'walk_frames' in sprites['left']:
            sprites['right']['walk_frames'] = [
                pg.transform.flip(frame, True, False)
                for frame in sprites['left']['walk_frames']
            ]
            sprites['right']['standing'] = sprites['right']['walk_frames'][-1]  # Последний кадр - стоячий

        # Проверяем, что все спрайты загружены, если нет - создаем заглушки
        for direction in sprites:
            if 'walk_frames' not in sprites[direction] or not sprites[direction]['walk_frames']:
                sprites[direction] = self._create_fallback_sprite(direction)
            if 'standing' not in sprites[direction]:
                sprites[direction]['standing'] = sprites[direction]['walk_frames'][0]

        return sprites

    def _load_sprite(self, filename):
        """Загружает один спрайт и масштабирует его до ВИЗУАЛЬНОГО размера"""
        # Поддерживаем оба расширения
        for ext in ['', '.png', '.PNG']:
            test_filename = filename.replace('.png', '').replace('.PNG', '') + ext
            file_path = os.path.join(self.project_root, 'Main', 'Sprites', 'Player', test_filename)

            try:
                if os.path.exists(file_path):
                    sprite = pg.image.load(file_path)

                    if sprite.get_alpha() is None:
                        sprite = sprite.convert()
                        bg_color = sprite.get_at((0, 0))
                        sprite.set_colorkey(bg_color)
                        sprite = sprite.convert_alpha()
                    else:
                        sprite = sprite.convert_alpha()

                    # Масштабируем до ВИЗУАЛЬНОГО размера
                    sprite = pg.transform.scale(sprite, (self.visual_size, self.visual_size))

                    print(f"Загружен: {test_filename}")
                    return sprite
            except Exception as e:
                continue

        print(f"Файл не найден: {filename}")
        return None

    def _create_fallback_sprite(self, direction):
        """Создает простой цветной спрайт-заглушку для отладки"""
        sprite = pg.Surface((self.visual_size, self.visual_size), pg.SRCALPHA)

        colors = {
            'down': (255, 0, 0, 255),
            'up': (0, 255, 0, 255),
            'left': (0, 0, 255, 255),
            'right': (255, 255, 0, 255)
        }

        sprite.fill(colors.get(direction, (255, 255, 255, 255)))

        center = self.visual_size // 2
        eye_color = (255, 255, 255)

        if direction == 'down':
            pg.draw.circle(sprite, eye_color, (center - 10, center + 5), 5)
            pg.draw.circle(sprite, eye_color, (center + 10, center + 5), 5)
        elif direction == 'up':
            pg.draw.circle(sprite, eye_color, (center - 10, center - 5), 5)
            pg.draw.circle(sprite, eye_color, (center + 10, center - 5), 5)
        else:
            pg.draw.circle(sprite, eye_color, (center - 10, center), 5)
            pg.draw.circle(sprite, eye_color, (center + 10, center), 5)

        return {
            'walk_frames': [sprite],
            'standing': sprite
        }

    def update(self, keys):
        dx, dy = 0, 0

        moving_up = keys[pg.K_w]
        moving_down = keys[pg.K_s]
        moving_left = keys[pg.K_a]
        moving_right = keys[pg.K_d]

        if moving_up:
            dy -= self.speed
            self.current_direction = 'up'
            self.is_moving = True
        elif moving_down:
            dy += self.speed
            self.current_direction = 'down'
            self.is_moving = True
        elif moving_left:
            dx -= self.speed
            self.current_direction = 'left'
            self.is_moving = True
        elif moving_right:
            dx += self.speed
            self.current_direction = 'right'
            self.is_moving = True
        else:
            self.is_moving = False

        # Движение с проверкой коллизий по ХИТБОКСУ
        if dx != 0:
            new_rect = self.rect.move(dx, 0)
            if self.map.is_walkable(new_rect):
                self.rect = new_rect

        if dy != 0:
            new_rect = self.rect.move(0, dy)
            if self.map.is_walkable(new_rect):
                self.rect = new_rect

        self._update_animation()

    def _update_animation(self):
        """Обновляет анимацию"""
        if self.is_moving:
            self.animation_timer += 1
            # Используем FPS для корректной скорости анимации
            if self.animation_timer >= self.animation_speed * 60:
                self.animation_timer = 0
                # Получаем количество кадров для текущего направления
                frames = self.sprites[self.current_direction]['walk_frames']
                max_frames = len(frames)
                self.current_frame = (self.current_frame + 1) % max_frames
        else:
            # Когда стоим на месте, показываем стоячий кадр (обычно последний)
            frames = self.sprites[self.current_direction]['walk_frames']
            self.current_frame = len(frames) - 1  # Последний кадр - стоячий
            self.animation_timer = 0

    def _get_current_sprite(self):
        """Возвращает текущий спрайт"""
        direction = self.sprites[self.current_direction]
        frames = direction['walk_frames']

        if self.current_frame < len(frames):
            return frames[self.current_frame]
        return frames[0]

    def render(self, screen, camera):
        """Отрисовка игрока (визуальный спрайт больше хитбокса)"""
        try:
            current_sprite = self._get_current_sprite()

            # Применяем камеру к ХИТБОКСУ
            screen_rect = camera.apply(self.rect)

            # Смещаем отрисовку, чтобы спрайт был по центру хитбокса
            offset_x = screen_rect.x - (self.visual_size - self.hitbox_size) // 2
            offset_y = screen_rect.y - (self.visual_size - self.hitbox_size) // 2

            screen.blit(current_sprite, (offset_x, offset_y))

        except Exception as e:
            screen_rect = camera.apply(self.rect)
            pg.draw.rect(screen, self.color, screen_rect)
            print(f"Ошибка отрисовки: {e}")


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

        self.head_rect = pg.Rect(
            self.base_head_x, self.base_head_y,
            self.head_size[0], self.head_size[1]
        )
        self.body_rect = pg.Rect(
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
                    original = pg.image.load(path)
                    self.head_sprite = pg.transform.scale(original, self.head_size)
                    print(f"Голова загружена: {self.head_size}")
                    break
                except:
                    continue

            for path in sprite_paths:
                try:
                    body_path = path.replace("head", "body")
                    original = pg.image.load(body_path)
                    self.body_sprite = pg.transform.scale(original, self.body_size)
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
            font = pg.font.Font(None, int(26 * self.ui_scale))

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

            self.dialogue_box_rect = pg.Rect(box_x, box_y, box_width, box_height)

            pg.draw.rect(screen, (0, 0, 0), self.dialogue_box_rect)
            pg.draw.rect(screen, (255, 255, 255), self.dialogue_box_rect, 2)

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
                tinted.fill((255, 0, 0, 100), special_flags=pg.BLEND_RGBA_MULT)
                screen.blit(tinted, self.body_rect)
            else:
                screen.blit(self.body_sprite, self.body_rect)
        else:
            color = (100, 50, 50) if self.flash_timer > 0 else (60, 30, 30)
            pg.draw.rect(screen, color, self.body_rect)
            pg.draw.rect(screen, (255, 255, 255), self.body_rect, 2)

        # Отрисовка головы ПОВЕРХ (спереди, перекрывает тело)
        if self.head_sprite:
            if self.flash_timer > 0:
                tinted = self.head_sprite.copy()
                tinted.fill((255, 0, 0, 100), special_flags=pg.BLEND_RGBA_MULT)
                screen.blit(tinted, self.head_rect)
            else:
                screen.blit(self.head_sprite, self.head_rect)
        else:
            color = (150, 50, 50) if self.flash_timer > 0 else (100, 30, 30)
            pg.draw.rect(screen, color, self.head_rect)
            pg.draw.rect(screen, (255, 255, 255), self.head_rect, 2)