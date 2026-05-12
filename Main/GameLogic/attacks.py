# attacks.py
import pygame
import random
import math


class AttackPattern:
    def __init__(self, arena_rect, duration, damage=1):
        self.arena = arena_rect
        self.duration = duration
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.active = True
        self.particles = []
        self.spawning_allowed = True  # Флаг разрешения спавна

    def update(self):
        pass

    def draw(self, screen):
        pass

    def check_collision(self, player_rect):
        return False

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.particles.append({
                'x': x, 'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'alpha': 255,
                'color': color,
                'size': random.randint(2, 5)
            })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] = max(0, particle['alpha'] - 8)
            if particle['alpha'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        for particle in self.particles:
            color_with_alpha = (*particle['color'], particle['alpha'])
            surf = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            surf.fill(color_with_alpha)
            screen.blit(surf, (particle['x'], particle['y']))

    def stop_spawning(self):
        """Останавливает спавн новых объектов"""
        self.spawning_allowed = False

    def destroy_all(self):
        pass


class FlyingBooks(AttackPattern):
    def __init__(self, arena_rect, duration=10000, damage=1, reduced=False):
        super().__init__(arena_rect, duration, damage)
        self.books = []
        self.spawn_timer = 0
        self.spawn_delay = 1500 if reduced else 1200
        self.max_books_per_spawn = 1 if reduced else 2

    def update(self):
        self.spawn_timer += 1
        self.update_particles()

        # Спавн только если разрешен
        if self.spawning_allowed and self.spawn_timer >= self.spawn_delay / 16.67:
            self.spawn_timer = 0
            for _ in range(random.randint(1, self.max_books_per_spawn)):
                self.spawn_book()

        for i, book in enumerate(self.books[:]):
            book['x'] += book['dx']
            book['y'] += book['dy']
            book['rotation'] += 3

            if book.get('spawning'):
                book['spawn_alpha'] = min(255, book['spawn_alpha'] + 30)
                book['spawn_scale'] = min(1.0, book['spawn_scale'] + 0.1)
                if book['spawn_alpha'] >= 255:
                    book['spawning'] = False

            # Столкновения между книгами
            for j, other_book in enumerate(self.books[:]):
                if i != j and not book.get('fading') and not other_book.get('fading'):
                    dx = book['x'] - other_book['x']
                    dy = book['y'] - other_book['y']
                    dist = math.sqrt(dx * dx + dy * dy)
                    min_dist = (book['size'] + other_book['size']) / 2
                    if dist < min_dist and dist > 0:
                        angle = math.atan2(dy, dx)
                        force = (min_dist - dist) * 0.5
                        book['x'] += math.cos(angle) * force
                        book['y'] += math.sin(angle) * force
                        other_book['x'] -= math.cos(angle) * force
                        other_book['y'] -= math.sin(angle) * force
                        book['dx'], other_book['dx'] = other_book['dx'] * 0.8, book['dx'] * 0.8
                        book['dy'], other_book['dy'] = other_book['dy'] * 0.8, book['dy'] * 0.8

            # Выход за границы - запускаем исчезновение
            margin = 60
            if (book['x'] < self.arena.left - margin or
                    book['x'] > self.arena.right + margin or
                    book['y'] < self.arena.top - margin or
                    book['y'] > self.arena.bottom + margin):
                if not book.get('fading') and not book.get('spawning'):
                    # Проверяем что книга прожила минимум 0.5 сек
                    if pygame.time.get_ticks() - book.get('spawn_time', 0) > 500:
                        book['fading'] = True
                        book['fade_alpha'] = 255

            if book.get('fading'):
                book['fade_alpha'] = max(0, book['fade_alpha'] - 20)
                if book['fade_alpha'] <= 0:
                    self.create_particles(book['x'], book['y'], book['color'])
                    self.books.remove(book)

    def spawn_book(self):
        side = random.choice(['left', 'right', 'top', 'bottom'])
        speed = random.uniform(0.6, 1.2)

        if side == 'left':
            x = self.arena.left - random.randint(40, 80)
            y = random.randint(self.arena.top, self.arena.bottom)
            dx = speed
            dy = random.uniform(-0.5, 0.5)
        elif side == 'right':
            x = self.arena.right + random.randint(40, 80)
            y = random.randint(self.arena.top, self.arena.bottom)
            dx = -speed
            dy = random.uniform(-0.5, 0.5)
        elif side == 'top':
            x = random.randint(self.arena.left, self.arena.right)
            y = self.arena.top - random.randint(40, 80)
            dx = random.uniform(-0.5, 0.5)
            dy = speed
        else:
            x = random.randint(self.arena.left, self.arena.right)
            y = self.arena.bottom + random.randint(40, 80)
            dx = random.uniform(-0.5, 0.5)
            dy = -speed

        self.books.append({
            'x': x, 'y': y,
            'dx': dx, 'dy': dy,
            'size': random.randint(35, 50),
            'color': (139, 69, 19),
            'rotation': random.randint(0, 360),
            'fading': False,
            'fade_alpha': 255,
            'spawning': True,
            'spawn_alpha': 0,
            'spawn_scale': 0.1,
            'spawn_time': pygame.time.get_ticks()
        })

    def check_collision(self, player_rect):
        for book in self.books[:]:
            if not book.get('fading') and not book.get('spawning'):
                book_rect = pygame.Rect(book['x'] - book['size'] // 2,
                                        book['y'] - book['size'] // 2,
                                        book['size'], book['size'])
                if player_rect.colliderect(book_rect):
                    book['fading'] = True
                    book['fade_alpha'] = 255
                    return True
        return False

    def stop_spawning(self):
        self.spawning_allowed = False

    def destroy_all(self):
        for book in self.books:
            if not book.get('fading'):
                book['fading'] = True
                book['fade_alpha'] = 255
                self.create_particles(book['x'], book['y'], book['color'])
        # Не очищаем список сразу - книги должны исчезнуть через fade

    def draw(self, screen):
        for book in self.books:
            alpha = book.get('fade_alpha', 255)
            spawn_alpha = book.get('spawn_alpha', 255)
            spawn_scale = book.get('spawn_scale', 1.0)
            final_alpha = min(alpha, spawn_alpha)
            current_size = int(book['size'] * spawn_scale)

            book_surf = pygame.Surface((current_size, int(current_size * 0.7)), pygame.SRCALPHA)
            color_with_alpha = (*book['color'], final_alpha)
            book_surf.fill(color_with_alpha)
            pygame.draw.rect(book_surf, (255, 255, 255, final_alpha),
                             (0, 0, current_size, int(current_size * 0.7)), 1)
            pygame.draw.line(book_surf, (255, 255, 255, final_alpha),
                             (3, int(current_size * 0.35)),
                             (current_size - 3, int(current_size * 0.35)), 1)
            book_surf = pygame.transform.rotate(book_surf, book['rotation'])
            book_rect = book_surf.get_rect(center=(book['x'], book['y']))
            screen.blit(book_surf, book_rect)
        self.draw_particles(screen)


class ExamPapers(AttackPattern):
    def __init__(self, arena_rect, duration=10000, damage=1, reduced=False):
        super().__init__(arena_rect, duration, damage)
        self.papers = []
        self.spawn_timer = 0
        self.spawn_delay = 1200 if reduced else 1000
        self.max_papers_per_spawn = 1 if reduced else 2
        self.paper_width = 42
        self.paper_height = 55

    def update(self):
        self.spawn_timer += 1
        self.update_particles()

        if self.spawning_allowed and self.spawn_timer >= self.spawn_delay / 16.67:
            self.spawn_timer = 0
            for _ in range(random.randint(1, self.max_papers_per_spawn)):
                self.spawn_paper()

        for paper in self.papers[:]:
            paper['y'] += paper['speed']
            paper['x'] += paper['drift']

            if paper.get('spawning'):
                paper['spawn_alpha'] = min(255, paper['spawn_alpha'] + 30)
                paper['spawn_scale'] = min(1.0, paper['spawn_scale'] + 0.1)
                if paper['spawn_alpha'] >= 255:
                    paper['spawning'] = False

            if paper['y'] > self.arena.bottom + 30:
                if not paper.get('fading') and not paper.get('spawning'):
                    paper['fading'] = True
                    paper['fade_alpha'] = 255

            if paper.get('fading'):
                paper['fade_alpha'] = max(0, paper['fade_alpha'] - 20)
                if paper['fade_alpha'] <= 0:
                    self.create_particles(paper['x'], paper['y'], paper['color'])
                    self.papers.remove(paper)

    def spawn_paper(self):
        x = random.randint(self.arena.left + 30, self.arena.right - 30)
        y = self.arena.top - random.randint(50, 120)
        speed = random.uniform(0.8, 1.5)
        drift = random.uniform(-0.3, 0.3)

        # Короткие надписи которые точно поместятся
        short_texts = ["WASD?", "2+2=?", "5/5"]
        # Для вертикального текста берем короткие слова
        long_texts = ["Экзамен", "Готов?", "Сдавай!"]

        use_vertical = random.choice([True, False])
        paper_text = random.choice(long_texts) if use_vertical else random.choice(short_texts)

        self.papers.append({
            'x': x, 'y': y,
            'speed': speed,
            'drift': drift,
            'color': (255, 255, 255),
            'fading': False,
            'fade_alpha': 255,
            'spawning': True,
            'spawn_alpha': 0,
            'spawn_scale': 0.1,
            'text': paper_text,
            'vertical': use_vertical
        })

    def check_collision(self, player_rect):
        for paper in self.papers[:]:
            if not paper.get('fading') and not paper.get('spawning'):
                paper_rect = pygame.Rect(paper['x'] - self.paper_width // 2,
                                         paper['y'] - self.paper_height // 2,
                                         self.paper_width, self.paper_height)
                if player_rect.colliderect(paper_rect):
                    paper['fading'] = True
                    paper['fade_alpha'] = 255
                    return True
        return False

    def stop_spawning(self):
        self.spawning_allowed = False

    def destroy_all(self):
        for paper in self.papers:
            if not paper.get('fading'):
                paper['fading'] = True
                paper['fade_alpha'] = 255
                self.create_particles(paper['x'], paper['y'], paper['color'])

    def draw(self, screen):
        for paper in self.papers:
            alpha = min(paper.get('fade_alpha', 255), paper.get('spawn_alpha', 255))
            scale = paper.get('spawn_scale', 1.0)
            current_w = int(self.paper_width * scale)
            current_h = int(self.paper_height * scale)

            paper_surf = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
            pygame.draw.rect(paper_surf, (*paper['color'], alpha), (0, 0, current_w, current_h))
            pygame.draw.rect(paper_surf, (0, 0, 0, alpha), (0, 0, current_w, current_h), 1)

            # Линии
            line_color = (180, 180, 255, alpha)
            for i in range(4):
                line_y = 10 + i * 10
                if line_y < current_h - 5:
                    pygame.draw.line(paper_surf, line_color, (3, line_y), (current_w - 3, line_y), 1)

            # Красное поле
            pygame.draw.line(paper_surf, (255, 100, 100, alpha), (10, 5), (10, current_h - 5), 1)

            if paper['vertical']:
                font = pygame.font.Font(None, max(12, int(current_w * 0.35)))
                text = paper['text']
                char_y = 8
                for char in text:
                    char_surf = font.render(char, True, (0, 0, 0, alpha))
                    if char_y + char_surf.get_height() < current_h - 5:
                        paper_surf.blit(char_surf, (current_w // 2 - char_surf.get_width() // 2, char_y))
                        char_y += char_surf.get_height() - 1
            else:
                # Горизонтальный текст - проверяем что помещается
                font = pygame.font.Font(None, max(10, int(current_h * 0.25)))
                text_surf = font.render(paper['text'], True, (0, 0, 0, alpha))
                # Если текст шире бумаги - уменьшаем шрифт
                if text_surf.get_width() > current_w - 15:
                    font = pygame.font.Font(None, max(8, int(current_h * 0.2)))
                    text_surf = font.render(paper['text'], True, (0, 0, 0, alpha))
                text_rect = text_surf.get_rect(center=(current_w // 2, current_h // 2))
                paper_surf.blit(text_surf, text_rect)

            paper_rect = paper_surf.get_rect(center=(paper['x'], paper['y']))
            screen.blit(paper_surf, paper_rect)
        self.draw_particles(screen)


# PointerLaser и FallingPapers - добавляем stop_spawning и destroy_all по тому же принципу
class PointerLaser(AttackPattern):
    def __init__(self, arena_rect, duration=10000, damage=1, reduced=False):
        super().__init__(arena_rect, duration, damage)
        self.lasers = []
        self.spawn_timer = 0
        self.spawn_delay = 1500 if reduced else 1200
        self.max_lasers = 2 if reduced else 3

    def update(self):
        self.spawn_timer += 1

        if self.spawning_allowed and self.spawn_timer >= self.spawn_delay / 16.67:
            self.spawn_timer = 0
            for _ in range(random.randint(1, self.max_lasers)):
                self.spawn_laser()

        for laser in self.lasers[:]:
            laser['warning_time'] -= 1
            if laser['warning_time'] <= 0 and not laser['active']:
                laser['active'] = True
                laser['alpha'] = 255
            if laser['active']:
                laser['duration'] -= 1
                laser['alpha'] = max(0, laser['alpha'] - 6)
                if laser['duration'] <= 0 or laser['alpha'] <= 0:
                    self.lasers.remove(laser)

    def spawn_laser(self):
        target_x = random.randint(self.arena.left + 20, self.arena.right - 20)
        self.lasers.append({
            'x': target_x, 'width': 15,
            'warning_time': random.randint(50, 70),
            'active': False, 'duration': random.randint(30, 45),
            'color': (255, 0, 0), 'alpha': 255
        })

    def check_collision(self, player_rect):
        for laser in self.lasers[:]:
            if laser['active']:
                laser_rect = pygame.Rect(laser['x'] - laser['width'] // 2,
                                         self.arena.top, laser['width'], self.arena.height)
                if player_rect.colliderect(laser_rect):
                    laser['alpha'] = 0
                    laser['duration'] = 0
                    return True
        return False

    def stop_spawning(self):
        self.spawning_allowed = False

    def destroy_all(self):
        self.lasers.clear()

    def draw(self, screen):
        for laser in self.lasers:
            if laser['active']:
                laser_surf = pygame.Surface((laser['width'], self.arena.height), pygame.SRCALPHA)
                laser_surf.fill((*laser['color'], laser['alpha']))
                screen.blit(laser_surf, (laser['x'] - laser['width'] // 2, self.arena.top))
                glow_surf = pygame.Surface((laser['width'] + 10, self.arena.height), pygame.SRCALPHA)
                glow_surf.fill((255, 100, 100, laser['alpha'] // 3))
                screen.blit(glow_surf, (laser['x'] - (laser['width'] + 10) // 2, self.arena.top))
            else:
                if pygame.time.get_ticks() % 500 < 250:
                    warn_surf = pygame.Surface((25, self.arena.height), pygame.SRCALPHA)
                    warn_surf.fill((255, 255, 0, 120))
                    screen.blit(warn_surf, (laser['x'] - 12, self.arena.top))


class FallingPapers(AttackPattern):
    def __init__(self, arena_rect, duration=10000, damage=1, reduced=False):
        super().__init__(arena_rect, duration, damage)
        self.papers = []
        self.spawn_timer = 0
        self.spawn_delay = 1300 if reduced else 1100
        self.paper_width = 50
        self.paper_height = 65

    def update(self):
        self.spawn_timer += 1
        self.update_particles()

        if self.spawning_allowed and self.spawn_timer >= self.spawn_delay / 16.67:
            self.spawn_timer = 0
            self.spawn_paper()

        for paper in self.papers[:]:
            paper['y'] += paper['speed']
            if paper.get('spawning'):
                paper['spawn_alpha'] = min(255, paper['spawn_alpha'] + 30)
                paper['spawn_scale'] = min(1.0, paper['spawn_scale'] + 0.1)
                if paper['spawn_alpha'] >= 255:
                    paper['spawning'] = False
            if paper['y'] > self.arena.bottom + 30:
                if not paper.get('fading') and not paper.get('spawning'):
                    paper['fading'] = True
                    paper['fade_alpha'] = 255
            if paper.get('fading'):
                paper['fade_alpha'] = max(0, paper['fade_alpha'] - 20)
                if paper['fade_alpha'] <= 0:
                    self.create_particles(paper['x'], paper['y'], paper['color'])
                    self.papers.remove(paper)

    def spawn_paper(self):
        x = random.randint(self.arena.left + 30, self.arena.right - 30)
        y = self.arena.top - random.randint(40, 100)
        speed = random.uniform(1.0, 2.0)
        questions = ["2+2=?", "WASD?", "√16=?", "3²=?", "Готов?", "Зачет?", "100%", "5/5"]
        self.papers.append({
            'x': x, 'y': y, 'speed': speed,
            'color': (255, 255, 220), 'fading': False, 'fade_alpha': 255,
            'spawning': True, 'spawn_alpha': 0, 'spawn_scale': 0.1,
            'question_text': random.choice(questions)
        })

    def check_collision(self, player_rect):
        for paper in self.papers[:]:
            if not paper.get('fading') and not paper.get('spawning'):
                paper_rect = pygame.Rect(paper['x'] - self.paper_width // 2,
                                         paper['y'] - self.paper_height // 2,
                                         self.paper_width, self.paper_height)
                if player_rect.colliderect(paper_rect):
                    paper['fading'] = True
                    paper['fade_alpha'] = 255
                    return True
        return False

    def stop_spawning(self):
        self.spawning_allowed = False

    def destroy_all(self):
        for paper in self.papers:
            if not paper.get('fading'):
                paper['fading'] = True
                paper['fade_alpha'] = 255
                self.create_particles(paper['x'], paper['y'], paper['color'])

    def draw(self, screen):
        for paper in self.papers:
            alpha = min(paper.get('fade_alpha', 255), paper.get('spawn_alpha', 255))
            scale = paper.get('spawn_scale', 1.0)
            current_w = int(self.paper_width * scale)
            current_h = int(self.paper_height * scale)
            paper_surf = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
            pygame.draw.rect(paper_surf, (*paper['color'], alpha), (0, 0, current_w, current_h))
            pygame.draw.rect(paper_surf, (0, 0, 0, alpha), (0, 0, current_w, current_h), 1)
            font = pygame.font.Font(None, max(12, int(current_h * 0.24)))
            text = font.render(paper['question_text'], True, (0, 0, 0, alpha))
            text_rect = text.get_rect(center=(current_w // 2, current_h // 2))
            paper_surf.blit(text, text_rect)
            if random.random() < 0.3:
                grade_font = pygame.font.Font(None, max(10, int(current_h * 0.22)))
                grade = grade_font.render("2", True, (255, 0, 0, alpha))
                paper_surf.blit(grade, (current_w - 12, 2))
            paper_rect = paper_surf.get_rect(center=(paper['x'], paper['y']))
            screen.blit(paper_surf, paper_rect)
        self.draw_particles(screen)


class CombinedAttack(AttackPattern):
    def __init__(self, arena_rect, duration=10000, damage=1, attack1=None, attack2=None):
        super().__init__(arena_rect, duration, damage)
        self.attack1 = attack1
        self.attack2 = attack2

    def update(self):
        if self.attack1:
            self.attack1.update()
        if self.attack2:
            self.attack2.update()

    def check_collision(self, player_rect):
        if self.attack1 and self.attack1.check_collision(player_rect):
            return True
        if self.attack2 and self.attack2.check_collision(player_rect):
            return True
        return False

    def stop_spawning(self):
        if self.attack1:
            self.attack1.stop_spawning()
        if self.attack2:
            self.attack2.stop_spawning()

    def destroy_all(self):
        if self.attack1:
            self.attack1.destroy_all()
        if self.attack2:
            self.attack2.destroy_all()

    def draw(self, screen):
        if self.attack1:
            self.attack1.draw(screen)
        if self.attack2:
            self.attack2.draw(screen)


# Оставлю здесь коммент |:)