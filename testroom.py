import pygame
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Получаем путь к директории, где находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Формируем полный путь к файлу карты
    map_path = os.path.join(script_dir, "map", "location1", "testlocation.tmx")

    print(f"Ищем карту по пути: {map_path}")  # Для отладки

    # Проверяем существование файла
    if not os.path.exists(map_path):
        print(f"Ошибка: файл карты не найден по пути {map_path}")
        print("Текущая рабочая директория:", os.getcwd())
        print("Директория скрипта:", script_dir)
        print("Содержимое директории map/location1:")
        map_dir = os.path.join(script_dir, "map", "location1")
        if os.path.exists(map_dir):
            print(os.listdir(map_dir))
        else:
            print(f"Директория {map_dir} не существует")
        return

    game_map = TiledMap(map_path, scale=4)

    spawn_x, spawn_y = game_map.find_spawn()
    player = Player(spawn_x, spawn_y, game_map)

    map_pixel_width = game_map.width * game_map.tilewidth
    map_pixel_height = game_map.height * game_map.tileheight
    camera = Camera(screen.get_width(), screen.get_height(),
                    map_pixel_width, map_pixel_height, scale=4)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)
        camera.update(player.rect)

        screen.fill((0, 0, 0))
        game_map.render(screen, camera)
        player.render(screen, camera)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()