# Ivanov_battle.py
# Второй уровень: бой с Ивановым с атаками (мини-играми)

import pygame as pg
import sys
import random
from logic import BattleUI, BattleMiniGame
from Main.entities.IvanovBoss import IvanovBoss
from HeartGraphGame import HeartGraphGame
from KuinaGame import KuinaGame
from LabyrinthGame import LabyrinthGame

# Импорт стандартных мини-игр (если недоступны, будут заменены)
try:
    from patterns import MovingWallGame, BonesFromFloorGame, DummyGame
except ImportError:
    MovingWallGame = BattleMiniGame
    BonesFromFloorGame = BattleMiniGame
    DummyGame = BattleMiniGame


def main():
    pg.init()
    pg.mixer.init()

    # --- ЗВУКИ ---
    BATTLE_MUSIC_PATH = "../soundtrack/alexander-nakarada-chase(chosic.com).mp3"
    BOSS_SPEAK_SOUND_PATH = "../Sounds/long-typing-on-the-keyboard.mp3"
    BUTTON_CLICK_SOUND_PATH = "../Sounds/mus_ohyes_1.mp3"

    try:
        pg.mixer.music.load(BATTLE_MUSIC_PATH)
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)
    except Exception as e:
        print("Не удалось загрузить фоновую музыку:", e)

    try:
        boss_speak_sound = pg.mixer.Sound(BOSS_SPEAK_SOUND_PATH)
        boss_speak_sound.set_volume(0.7)
    except Exception as e:
        print("Не удалось загрузить звук речи босса:", e)
        boss_speak_sound = None

    try:
        button_click_sound = pg.mixer.Sound(BUTTON_CLICK_SOUND_PATH)
        button_click_sound.set_volume(0.6)
    except Exception as e:
        print("Не удалось загрузить звук кнопки:", e)
        button_click_sound = None

    info = pg.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pg.display.set_mode((screen_width, screen_height), pg.FULLSCREEN)
    pg.display.set_caption("Ivanov Boss Battle – Уровень 2 (с атаками)")
    clock = pg.time.Clock()

    UI_SCALE = min(screen_width / 800, screen_height / 600)

    # --- UI ---
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

    # --- БОСС (ИВАНОВ) ---
    boss = IvanovBoss(screen, battle_ui, UI_SCALE)
    boss_hp_max = 100
    boss_hp_current = boss_hp_max

    battle_ui.set_initial_message("Появился ИВАНОВ! (Уровень 2 – есть атаки)")
    boss.show_dialogue([
        "Слушай внимательно, студент...",
        "Используй WASD для движения!",
        "Уклоняйся от моих атак!",
        "Атакуй, когда будешь готов!"
    ])
    if boss_speak_sound:
        boss_speak_sound.play()

    # --- СОСТОЯНИЯ БОЯ ---
    STATE_MAIN = 0
    STATE_ACTION = 1
    STATE_SHRINK_HOR = 2
    STATE_BATTLE = 3
    current_state = STATE_MAIN

    act_buttons = ["ПОГОВОРИТЬ", "ПОЖАЛЕТЬ", "ПРОВЕРИТЬ", "НАЗАД"]

    # --- НАСТРОЙКА АНИМАЦИИ СЖАТИЯ ПОЛЯ ---
    original_buttons_y = battle_ui.original_main_buttons_y
    target_buttons_y = screen.get_height() + battle_ui.button_height
    original_text_rect = battle_ui.text_area_rect.copy()

    WIDE_WIDTH = int(screen_width * 0.7)
    NARROW_WIDTH = int(300 * UI_SCALE)
    screen_center_x = screen_width // 2
    battle_ui.text_area_rect.width = WIDE_WIDTH
    battle_ui.text_area_rect.centerx = screen_center_x
    original_center_x = battle_ui.text_area_rect.centerx

    shrink_duration = 500
    shrink_start_time = 0

    def start_shrink_animation():
        nonlocal current_state, shrink_start_time
        current_state = STATE_SHRINK_HOR
        shrink_start_time = pg.time.get_ticks()
        battle_ui.current_messages = []
        battle_ui.disable_input()

    def start_boss_attack():
        nonlocal current_state
        arena = battle_ui.text_area_rect.copy()
        minigame = HeartGraphGame(
            battle_ui, arena,
            duration=30000,  # 30 секунд
            enemy_damage=5,
            red_interval=2000,
            damage_cooldown=500,
            num_red_nodes=2
        )
        boss.start_attack("Сердечный граф", minigame)
        current_state = STATE_BATTLE

    running = True

    while running:
        mouse_clicked = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_clicked = True

            # Если мы в мини-игре, передаём событие ей
            if current_state == STATE_BATTLE and boss.current_minigame:
                boss.current_minigame.handle_event(event)
                continue

            result = battle_ui.handle_event(event)

            if result >= 0 or result >= 1000:
                if button_click_sound:
                    button_click_sound.play()

            if result == -2:  # ESC
                if current_state == STATE_ACTION:
                    battle_ui.clear_popup_buttons()
                    battle_ui.restore_initial()
                    current_state = STATE_MAIN

            # --- ОСНОВНОЕ МЕНЮ ---
            if current_state == STATE_MAIN and 0 <= result < 4:
                if result == 0:  # АТАКА
                    damage = random.randint(10, 25)
                    boss_hp_current = max(0, boss_hp_current - damage)
                    battle_ui.add_message(f"Ты нанёс {damage} урона!")
                    boss.take_damage(damage)

                    # Смена фаз
                    if boss_hp_current <= boss_hp_max * 0.3 and boss.phase == 2:
                        boss.phase = 3
                        battle_ui.add_message("ФАЗА 3!")
                        boss.show_dialogue([
                            "АРГХ! ФИНАЛЬНАЯ ФАЗА!",
                            "Покажи всё, чему научился!",
                            "WASD - твои лучшие друзья!"
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                    elif boss_hp_current <= boss_hp_max * 0.6 and boss.phase == 1:
                        boss.phase = 2
                        battle_ui.add_message("ФАЗА 2!")
                        boss.show_dialogue([
                            "Неплохо... Переходим ко второй фазе!",
                            "Атаки станут быстрее!",
                            "Используй все клавиши WASD!",
                            "Двигайся по всей арене!"
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()

                    if boss_hp_current > 0:
                        start_shrink_animation()
                    else:
                        boss.show_dialogue([
                            "Как... Ты победил меня...",
                            "Ты отлично двигался, студент!"
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                        pg.time.wait(3000)
                        running = False

                elif result == 1:  # ДЕЙСТВИЕ
                    battle_ui.set_popup_buttons(act_buttons, layout='horizontal', padding=int(5 * UI_SCALE))
                    battle_ui.set_message("Выбери действие:")
                    current_state = STATE_ACTION

                elif result == 2:  # ПРЕДМЕТЫ
                    battle_ui.add_message("У тебя нет предметов.")
                    boss.show_dialogue(["Предметы? Здесь только твои навыки!"])
                    if boss_speak_sound:
                        boss_speak_sound.play()

                elif result == 3:  # ПОЩАДА
                    if boss_hp_current < boss_hp_max // 2:
                        if random.random() < 0.3:
                            boss.show_dialogue([
                                "Хорошо, ты проявил милосердие...",
                                "Ты научился не только сражаться!"
                            ])
                            if boss_speak_sound:
                                boss_speak_sound.play()
                            battle_ui.add_message("Ты пощадил Иванова!")
                            running = False
                        else:
                            boss.show_dialogue([
                                "Не дождёшься! Продолжай бой!",
                                "Покажи свою силу!"
                            ])
                            if boss_speak_sound:
                                boss_speak_sound.play()
                    else:
                        battle_ui.add_message("Сначала ослабь врага!")
                        boss.show_dialogue([
                            "Сначала ослабь меня!",
                            "Моё HP должно быть ниже 50%"
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()

            # --- МЕНЮ ДЕЙСТВИЙ ---
            elif current_state == STATE_ACTION and result >= 1000:
                action = act_buttons[result - 1000]
                battle_ui.clear_popup_buttons()
                battle_ui.restore_initial()

                if action == "НАЗАД":
                    current_state = STATE_MAIN
                else:
                    if action == "ПОГОВОРИТЬ":
                        boss.show_dialogue([
                            "Что? Некогда болтать!",
                            "Уклоняйся лучше!",
                            "WASD используй активно!"
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                    elif action == "ПОЖАЛЕТЬ":
                        battle_ui.add_message("Ты проявляешь сострадание...")
                        boss.show_dialogue([
                            "Жалость? В бою нет жалости!",
                            "Но твоя доброта замечена..."
                        ])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                    elif action == "ПРОВЕРИТЬ":
                        battle_ui.add_message(f"ИВАНОВ - Обучающий босс (Фаза {boss.phase})")
                        boss_phase_hints = {
                            1: "Использует базовые атаки. Управление: WASD",
                            2: "Атаки становятся быстрее! Двигайся активнее!",
                            3: "Финальная фаза! Не стой на месте!"
                        }
                        battle_ui.add_message(boss_phase_hints.get(boss.phase, ""))
                        battle_ui.add_message("Управление: WASD для движения")

                    current_state = STATE_MAIN
                    if boss_hp_current > 0:
                        start_shrink_animation()

        # --- ДИАЛОГИ ПО КЛИКУ ---
        if mouse_clicked and boss.current_dialogue:
            if boss.dialogue_char_index >= len(boss.current_dialogue):
                if boss.dialogue_queue:
                    boss.display_next_dialogue()
                else:
                    boss.dialogue_done = True

        # --- АНИМАЦИЯ СЖАТИЯ ПОЛЯ ---
        if current_state == STATE_SHRINK_HOR:
            elapsed = pg.time.get_ticks() - shrink_start_time
            progress = min(elapsed / shrink_duration, 1.0)
            new_width = WIDE_WIDTH - (WIDE_WIDTH - NARROW_WIDTH) * progress
            battle_ui.text_area_rect.width = int(new_width)
            battle_ui.text_area_rect.centerx = original_center_x
            new_y = original_buttons_y + (target_buttons_y - original_buttons_y) * progress
            battle_ui.set_main_buttons_y(new_y)
            if progress >= 1.0:
                start_boss_attack()

        # --- ОБНОВЛЕНИЕ БОССА ---
        boss.update()

        # --- ЗАВЕРШЕНИЕ МИНИ-ИГРЫ ---
        if current_state == STATE_BATTLE and boss.current_minigame:
            if boss.current_minigame.is_finished():
                victory = boss.current_minigame.is_victory()
                game_type = type(boss.current_minigame).__name__
                print(f"[DEBUG] Завершена {game_type}, victory={victory}")

                if victory and game_type == "HeartGraphGame":
                    print("[DEBUG] Запускаем KuinaGame")
                    arena = battle_ui.text_area_rect.copy()
                    if arena.width < 50 or arena.height < 50:
                        arena = pg.Rect(100, 100, 600, 400)
                    kuina = KuinaGame(battle_ui, arena, target_count=10, time_limit=30000, enemy_damage=5)
                    boss.current_minigame = kuina
                    boss.current_pattern = "WASD-догонялки"

                elif victory and game_type == "KuinaGame":
                    print("[DEBUG] Запускаем LabyrinthGame")
                    arena = battle_ui.text_area_rect.copy()
                    if arena.width < 50 or arena.height < 50:
                        arena = pg.Rect(100, 100, 600, 400)
                    labyrinth = LabyrinthGame(battle_ui, arena, scroll_count=5, time_limit=40000, wall_damage=1)
                    boss.current_minigame = labyrinth
                    boss.current_pattern = "Лабиринт знаний"

                else:
                    boss.end_attack()
                    if victory:
                        battle_ui.add_message("Все испытания пройдены!")
                        boss.show_dialogue(["Ты победил!", "Отличная работа!"])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                    else:
                        battle_ui.add_message("Ты проиграл мини-игру...")
                        boss.show_dialogue(["Не повезло...", "Попробуй ещё раз!"])
                        if boss_speak_sound:
                            boss_speak_sound.play()
                    current_state = STATE_MAIN

        # --- ПРОВЕРКА ПОРАЖЕНИЯ ИГРОКА ---
        if battle_ui.current_hp <= 0:
            boss.show_dialogue([
                "Ты проиграл, студент...",
                "Но ты можешь попробовать снова!",
                "Помни: WASD - движение!"
            ])
            if boss_speak_sound:
                boss_speak_sound.play()
            battle_ui.add_message("ТЫ ПОВЕРЖЕН... GAME OVER")
            battle_ui.draw()
            pg.display.flip()
            pg.time.wait(3000)
            running = False

        # --- ОТРИСОВКА ---
        if current_state != STATE_BATTLE:
            battle_ui.draw()
            font = pg.font.Font(None, int(36 * UI_SCALE))
            name_text = font.render(boss.name, True, (0, 0, 0))
            name_rect = name_text.get_rect(centerx=screen_width // 2, top=int(10 * UI_SCALE))
            screen.blit(name_text, name_rect.move(2, 2))
            name_text = font.render(boss.name, True, (255, 255, 255))
            screen.blit(name_text, name_rect)
        else:
            screen.fill((0, 0, 0))

        boss.draw(screen)
        if boss.current_dialogue:
            boss.draw_dialogue_box(screen)

        if boss.current_minigame:
            boss.current_minigame.draw(screen)

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()