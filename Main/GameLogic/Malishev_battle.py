import os
import pygame as pg
import sys
import random
from Main.GameLogic.logic import BattleUI
from Main.GameLogic.MainGameClasses import MalishevBoss
from Main.GameLogic.attacks import FlyingBooks, ExamPapers, PointerLaser, FallingPapers, CombinedAttack


def run_boss_battle(screen):
    """Запускает битву с боссом и возвращает True при победе, False при поражении"""

    # Получаем корневую директорию проекта для правильных путей к звукам
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    info = pg.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    clock = pg.time.Clock()

    # ===== ЗВУКИ =====
    BATTLE_MUSIC_PATH = os.path.join(project_root, "soundtrack", "alexander-nakarada-chase(chosic.com).mp3")
    BOSS_SPEAK_SOUND_PATH = os.path.join(project_root, "Sounds", "long-typing-on-the-keyboard.mp3")
    BUTTON_CLICK_SOUND_PATH = os.path.join(project_root, "Sounds", "mus_ohyes_1.mp3")

    # Фоновая музыка
    try:
        pg.mixer.music.load(BATTLE_MUSIC_PATH)
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)
    except Exception as e:
        print("Не удалось загрузить фоновую музыку:", e)

    # Звук речи босса
    try:
        boss_speak_sound = pg.mixer.Sound(BOSS_SPEAK_SOUND_PATH)
        boss_speak_sound.set_volume(0.7)
    except Exception as e:
        print("Не удалось загрузить звук речи босса:", e)
        boss_speak_sound = None

    # Звук клика по кнопке
    try:
        button_click_sound = pg.mixer.Sound(BUTTON_CLICK_SOUND_PATH)
        button_click_sound.set_volume(0.6)
    except Exception as e:
        print("Не удалось загрузить звук кнопки:", e)
        button_click_sound = None

    UI_SCALE = min(screen_width / 800, screen_height / 600)

    battle_ui = BattleUI(
        screen,
        main_buttons=["АТАКА", "ДЕЙСТВИЕ", "ПРЕДМЕТЫ", "ПОЩАДА"],
        font_path="Anderfefu/fonts/SMB1NESClassix-Regular.otf",
        font_size=int(14 * UI_SCALE),
        text_color=(255, 255, 255),
        button_outline_color=(255, 255, 255),
        button_bg_color=(0, 0, 0),
        bg_color=(0, 0, 0),
        button_height=int(55 * UI_SCALE),
        button_spacing=int(20 * UI_SCALE),
        text_area_height=int(100 * UI_SCALE),
        text_area_bottom_margin=int(3 * UI_SCALE),
        max_hp=20,
        current_hp=20,
        health_bar_height=int(20 * UI_SCALE),
        health_bar_color=(255, 255, 0),
        health_bar_outline=(255, 255, 255),
    )

    # Отключаем текст
    battle_ui.current_messages = []
    battle_ui.initial_message = ""

    def dummy(*args, **kwargs):
        pass

    battle_ui.add_message = dummy
    battle_ui.set_message = dummy
    battle_ui.set_initial_message = dummy

    boss = MalishevBoss(screen, battle_ui, UI_SCALE)

    player_rect = pg.Rect(0, 0, 20, 20)
    player_rect.centerx = battle_ui.text_area_rect.centerx
    player_rect.centery = battle_ui.text_area_rect.centery
    player_color = (255, 0, 0)
    player_speed = 5
    show_player = False

    boss.patterns = {
        1: ["Летающие книги", "Экзаменационные листы", "Лазерная указка"],
        2: ["Летающие книги", "Экзаменационные листы", "Лазерная указка",
            "Падающие листы", "Книги + Лазер", "Книги + Листы"],
        3: ["Летающие книги", "Экзаменационные листы", "Лазерная указка",
            "Падающие листы", "Книги + Лазер", "Книги + Листы", "Лазер + Падающие"]
    }

    boss_battle_quotes = [
        "Хорошо двигаешься!", "Не останавливайся!", "Используй WASD!",
        "Уклоняйся!", "Хорошая реакция!", "Продолжай двигаться!",
        "Не стой на месте!", "Следи за атаками!", "Отлично!", "Молодец, студент!"
    ]

    boss_hp_max = 100
    boss_hp_current = boss_hp_max

    # Функция для воспроизведения звука речи
    def play_boss_sound():
        if boss_speak_sound:
            boss_speak_sound.play()

    # Начальный диалог со звуком
    boss.show_dialogue([
        "Слушай внимательно, студент...",
        "Используй WASD для движения!",
        "Уклоняйся от моих атак!",
        "Продержись 30 секунд!"
    ])
    play_boss_sound()

    STATE_MAIN = 0
    STATE_ACTION = 1
    STATE_SHRINK_HOR = 2
    STATE_BATTLE = 3
    current_state = STATE_MAIN

    current_attack_name = ""
    attack_timer = 0
    attack_duration = 10000

    PHASE_ATTACK = 0
    PHASE_DESTROY = 1
    PHASE_PAUSE = 2
    switch_phase = PHASE_ATTACK
    switch_timer = 0
    DESTROY_TIME = 800
    PAUSE_TIME = 500
    next_attack_name = ""

    dialogue_cooldown = 0
    dialogue_cooldown_time = 2000

    act_buttons = ["ПОГОВОРИТЬ", "ПОЖАЛЕТЬ", "ПРОВЕРИТЬ", "НАЗАД"]

    original_buttons_y = battle_ui.original_main_buttons_y
    target_buttons_y = screen.get_height() + battle_ui.button_height

    WIDE_WIDTH = int(screen_width * 0.7)
    NARROW_WIDTH = int(300 * UI_SCALE)

    screen_center_x = screen_width // 2
    battle_ui.text_area_rect.width = WIDE_WIDTH
    battle_ui.text_area_rect.centerx = screen_center_x
    original_text_rect = battle_ui.text_area_rect.copy()
    original_center_x = original_text_rect.centerx

    shrink_duration = 500
    shrink_start_time = 0

    quote_timer = 0
    quote_interval = 5000

    battle_start_time = 0
    total_battle_duration = 30000

    end_phase = False
    end_timer = 0

    victory = False

    def reset_player_position():
        player_rect.centerx = battle_ui.text_area_rect.centerx
        player_rect.centery = battle_ui.text_area_rect.centery

    def start_shrink_animation():
        nonlocal current_state, shrink_start_time
        current_state = STATE_SHRINK_HOR
        shrink_start_time = pg.time.get_ticks()
        battle_ui.disable_input()

    def create_attack(pattern_name):
        arena = battle_ui.text_area_rect.copy()
        if pattern_name == "Летающие книги":
            return FlyingBooks(arena, duration=10000, damage=1)
        elif pattern_name == "Экзаменационные листы":
            return ExamPapers(arena, duration=10000, damage=1)
        elif pattern_name == "Лазерная указка":
            return PointerLaser(arena, duration=10000, damage=1)
        elif pattern_name == "Падающие листы":
            return FallingPapers(arena, duration=10000, damage=1)
        elif pattern_name == "Книги + Лазер":
            return CombinedAttack(arena, duration=10000, damage=1,
                                  attack1=FlyingBooks(arena, duration=10000, damage=1, reduced=True),
                                  attack2=PointerLaser(arena, duration=10000, damage=1, reduced=True))
        elif pattern_name == "Книги + Листы":
            return CombinedAttack(arena, duration=10000, damage=1,
                                  attack1=FlyingBooks(arena, duration=10000, damage=1, reduced=True),
                                  attack2=ExamPapers(arena, duration=10000, damage=1, reduced=True))
        elif pattern_name == "Лазер + Падающие":
            return CombinedAttack(arena, duration=10000, damage=1,
                                  attack1=PointerLaser(arena, duration=10000, damage=1, reduced=True),
                                  attack2=FallingPapers(arena, duration=10000, damage=1, reduced=True))
        return FlyingBooks(arena, duration=10000, damage=1)

    def start_battle():
        nonlocal current_state, current_attack_name, attack_timer, battle_start_time, switch_phase, end_phase
        battle_start_time = pg.time.get_ticks()
        switch_phase = PHASE_ATTACK
        attack_timer = 0
        end_phase = False
        current_attack_name = random.choice(boss.patterns[boss.phase])
        minigame = create_attack(current_attack_name)
        boss.start_attack(current_attack_name, minigame)
        current_state = STATE_BATTLE

    running = True
    while running:
        battle_ui.current_messages = []
        mouse_clicked = False
        keys = pg.key.get_pressed()

        if dialogue_cooldown > 0:
            dialogue_cooldown -= clock.get_time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                victory = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_clicked = True

            result = battle_ui.handle_event(event)

            if result == -2:
                if current_state == STATE_ACTION:
                    battle_ui.clear_popup_buttons()
                    battle_ui.restore_initial()
                    current_state = STATE_MAIN

            if current_state == STATE_MAIN and 0 <= result < 4:
                if result == 0:
                    damage = random.randint(10, 25)
                    boss_hp_current = max(0, boss_hp_current - damage)
                    boss.take_damage(damage)

                    if boss_hp_current <= boss_hp_max * 0.3 and boss.phase == 2:
                        boss.phase = 3
                        boss.show_dialogue(["АРГХ! ФИНАЛЬНАЯ ФАЗА!"])
                        dialogue_cooldown = dialogue_cooldown_time
                        play_boss_sound()
                    elif boss_hp_current <= boss_hp_max * 0.6 and boss.phase == 1:
                        boss.phase = 2
                        boss.show_dialogue(["Неплохо... Вторая фаза!"])
                        dialogue_cooldown = dialogue_cooldown_time
                        play_boss_sound()

                    if boss_hp_current > 0:
                        start_shrink_animation()
                    else:
                        boss.show_dialogue(["Ты победил меня!"])
                        play_boss_sound()
                        pg.time.wait(3000)
                        victory = True
                        running = False

                elif result == 1:
                    battle_ui.set_popup_buttons(act_buttons, layout='horizontal', padding=int(5 * UI_SCALE))
                    current_state = STATE_ACTION

                elif result == 2:
                    boss.show_dialogue(["Предметы? Здесь только твои навыки!"])
                    dialogue_cooldown = dialogue_cooldown_time
                    play_boss_sound()

                elif result == 3:
                    if boss_hp_current < boss_hp_max // 2:
                        if random.random() < 0.3:
                            boss.show_dialogue(["Ты пощадил меня!"])
                            play_boss_sound()
                            victory = True
                            running = False
                        else:
                            boss.show_dialogue(["Не дождёшься!"])
                            dialogue_cooldown = dialogue_cooldown_time
                            play_boss_sound()
                    else:
                        boss.show_dialogue(["Сначала ослабь меня!"])
                        dialogue_cooldown = dialogue_cooldown_time
                        play_boss_sound()

            elif current_state == STATE_ACTION and result >= 1000:
                action = act_buttons[result - 1000]
                battle_ui.clear_popup_buttons()
                battle_ui.restore_initial()
                if action == "НАЗАД":
                    current_state = STATE_MAIN
                else:
                    if action == "ПОГОВОРИТЬ":
                        boss.show_dialogue(["Что? Некогда болтать!"])
                        play_boss_sound()
                    elif action == "ПОЖАЛЕТЬ":
                        boss.show_dialogue(["Жалость? В бою нет жалости!"])
                        play_boss_sound()
                    elif action == "ПРОВЕРИТЬ":
                        boss.show_dialogue([boss_phase_hints[boss.phase]])
                        play_boss_sound()
                    dialogue_cooldown = dialogue_cooldown_time
                    current_state = STATE_MAIN
                    if boss_hp_current > 0:
                        start_shrink_animation()

        # Движение игрока
        if current_state == STATE_BATTLE and show_player and not end_phase:
            if keys[pg.K_w]: player_rect.y -= player_speed
            if keys[pg.K_s]: player_rect.y += player_speed
            if keys[pg.K_a]: player_rect.x -= player_speed
            if keys[pg.K_d]: player_rect.x += player_speed
            arena = battle_ui.text_area_rect
            player_rect.clamp_ip(arena)

            if boss.current_minigame and switch_phase == PHASE_ATTACK:
                if boss.current_minigame.check_collision(player_rect):
                    new_hp = max(0, battle_ui.current_hp - boss.current_minigame.damage)
                    battle_ui.set_hp(new_hp, battle_ui.max_hp)
                    player_rect.y -= 10

        if mouse_clicked and boss.current_dialogue:
            if boss.dialogue_char_index >= len(boss.current_dialogue):
                if boss.dialogue_queue:
                    boss.display_next_dialogue()
                    play_boss_sound()
                else:
                    boss.dialogue_done = True

        # Анимация сжатия
        if current_state == STATE_SHRINK_HOR:
            show_player = True
            elapsed = pg.time.get_ticks() - shrink_start_time
            progress = min(elapsed / shrink_duration, 1.0)
            new_width = WIDE_WIDTH - (WIDE_WIDTH - NARROW_WIDTH) * progress
            battle_ui.text_area_rect.width = int(new_width)
            battle_ui.text_area_rect.centerx = original_center_x
            new_y = original_buttons_y + (target_buttons_y - original_buttons_y) * progress
            battle_ui.set_main_buttons_y(new_y)
            if progress >= 1.0:
                start_battle()

        # Логика боя
        if current_state == STATE_BATTLE and not end_phase:
            elapsed_total = pg.time.get_ticks() - battle_start_time

            if elapsed_total >= total_battle_duration:
                end_phase = True
                end_timer = 0
                victory = True
                if boss.current_minigame and hasattr(boss.current_minigame, 'destroy_all'):
                    boss.current_minigame.destroy_all()
                continue

            if boss.current_minigame:
                boss.current_minigame.update()

            if switch_phase == PHASE_ATTACK:
                attack_timer += clock.get_time()

                quote_timer += clock.get_time()
                if quote_timer >= quote_interval and dialogue_cooldown <= 0:
                    quote_timer = 0
                    boss.show_dialogue([random.choice(boss_battle_quotes)])
                    dialogue_cooldown = dialogue_cooldown_time
                    play_boss_sound()

                if attack_timer >= attack_duration:
                    if hasattr(boss.current_minigame, 'stop_spawning'):
                        boss.current_minigame.stop_spawning()
                    if hasattr(boss.current_minigame, 'destroy_all'):
                        boss.current_minigame.destroy_all()

                    available = boss.patterns[boss.phase].copy()
                    if current_attack_name in available and len(available) > 1:
                        available.remove(current_attack_name)
                    next_attack_name = random.choice(available)

                    switch_phase = PHASE_DESTROY
                    switch_timer = 0

                    if dialogue_cooldown <= 0:
                        boss.show_dialogue(["Следующая атака!"])
                        dialogue_cooldown = dialogue_cooldown_time
                        play_boss_sound()

            elif switch_phase == PHASE_DESTROY:
                switch_timer += clock.get_time()
                if switch_timer >= DESTROY_TIME:
                    switch_phase = PHASE_PAUSE
                    switch_timer = 0

            elif switch_phase == PHASE_PAUSE:
                switch_timer += clock.get_time()
                if switch_timer >= PAUSE_TIME:
                    new_minigame = create_attack(next_attack_name)
                    current_attack_name = next_attack_name
                    boss.start_attack(next_attack_name, new_minigame)
                    attack_timer = 0
                    switch_phase = PHASE_ATTACK

        # Конец боя
        if end_phase:
            if boss.current_minigame:
                boss.current_minigame.update()
            end_timer += clock.get_time()
            if end_timer >= 1000:
                show_player = False
                battle_ui.text_area_rect.width = WIDE_WIDTH
                battle_ui.text_area_rect.centerx = original_center_x
                battle_ui.set_main_buttons_y(original_buttons_y)
                battle_ui.enable_input()
                reset_player_position()
                boss.end_attack()
                current_state = STATE_MAIN
                end_phase = False

        boss.update()

        if battle_ui.current_hp <= 0:
            boss.show_dialogue(["Ты проиграл..."])
            play_boss_sound()
            pg.time.wait(3000)
            victory = False
            running = False

        # Отрисовка
        battle_ui.draw()
        boss.draw(screen)

        if show_player:
            pg.draw.circle(screen, player_color, player_rect.center, player_rect.width // 2)
            pg.draw.circle(screen, (255, 255, 255), player_rect.center, player_rect.width // 2, 2)

        if boss.current_dialogue:
            boss.draw_dialogue_box(screen)

        font = pg.font.Font(None, int(36 * UI_SCALE))
        name_text = font.render(boss.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(centerx=screen_width // 2, top=int(10 * UI_SCALE))
        screen.blit(name_text, name_rect)

        if boss.current_minigame and show_player:
            if not end_phase:
                remaining = max(0, total_battle_duration - (pg.time.get_ticks() - battle_start_time))
                seconds = remaining // 1000
                timer_font = pg.font.Font(None, int(24 * UI_SCALE))
                timer_text = timer_font.render(f"Время: {seconds}с", True, (255, 255, 255))
                screen.blit(timer_text, (battle_ui.text_area_rect.centerx - 40, battle_ui.text_area_rect.top - 25))
            boss.current_minigame.draw(screen)

        pg.display.flip()
        clock.tick(60)

    # Останавливаем музыку после боя
    pg.mixer.music.stop()
    return victory


boss_phase_hints = {
    1: "Атаки: Книги, листы и лазер. WASD",
    2: "Добавлены комбо-атаки!",
    3: "Финальная фаза!"
}