# test_battle.py
import pygame as pg
import sys
from logic import BattleUI, BattleMiniGame
import random

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("TEST ROOM with Health Bar")
    clock = pg.time.Clock()

    battle_ui = BattleUI(
        screen,
        main_buttons=["СПИСАТЬ", "ДЕЙСТВИЕ", "ПРЕДМЕТЫ", "ДУМАТЬ"],
        font_path="Anderfefu/fonts/SMB1NESClassix-Regular.otf",
        font_size=10,
        text_color=(255, 255, 255),
        button_outline_color=(255, 255, 255),
        button_bg_color=(0, 0, 0),
        bg_color=(0, 0, 0),
        button_height=80,
        button_spacing=20,
        text_area_height=150,
        text_area_bottom_margin=3,
        max_hp=20,
        current_hp=20,
        health_bar_height=20,
        health_bar_color=(255, 255, 0),
        health_bar_outline=(255, 255, 255),
    )

    battle_ui.set_initial_message("Враг появился! Твой ход. Выбери действие.")

    original_buttons_y = battle_ui.original_main_buttons_y
    target_buttons_y = screen.get_height() + battle_ui.button_height
    original_text_rect = battle_ui.text_area_rect.copy()

    STATE_MAIN = 0
    STATE_ACTION = 1
    STATE_RESULT_SHOW = 2
    STATE_SHRINK_HOR = 3
    STATE_BATTLE = 4
    current_state = STATE_MAIN

    shrink_duration = 500
    shrink_start_time = 0
    original_center_x = original_text_rect.centerx
    original_width = original_text_rect.width
    shrink_target_width = 400

    action_buttons = ["АТАКА", "ЗАЩИТА", "МАГИЯ", "НАЗАД"]
    action_results = {
        "АТАКА": "Ты атаковал! Враг готовится к ответу...",
        "ЗАЩИТА": "Ты встал в защитную стойку...",
        "МАГИЯ": "Ты начал читать заклинание..."
    }

    mini_game = None

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break

            if current_state == STATE_BATTLE and mini_game:
                mini_game.handle_event(event)
                continue

            result = battle_ui.handle_event(event)

            if result == -2:
                if current_state == STATE_SHRINK_HOR:
                    battle_ui.text_area_rect = original_text_rect.copy()
                    battle_ui.set_main_buttons_y(original_buttons_y)
                    battle_ui.clear_popup_buttons()
                    battle_ui.restore_initial()
                    battle_ui.enable_input()
                    current_state = STATE_MAIN
                elif current_state == STATE_RESULT_SHOW:
                    battle_ui.restore_initial()
                    current_state = STATE_MAIN
                elif current_state == STATE_ACTION:
                    battle_ui.clear_popup_buttons()
                    battle_ui.restore_initial()
                    current_state = STATE_MAIN

            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if current_state == STATE_RESULT_SHOW:
                    current_state = STATE_SHRINK_HOR
                    shrink_start_time = pg.time.get_ticks()
                    battle_ui.current_messages = []
                    battle_ui.disable_input()

            if result != -1 and result != -2:
                if current_state == STATE_MAIN and result < 1000:
                    if result == 0:  # СПИСАТЬ
                        # Больше не отнимаем HP, только сообщение
                        battle_ui.set_message("Списывание не удалось!  (Нажми Enter)")
                        current_state = STATE_RESULT_SHOW
                    elif result == 1:  # ДЕЙСТВИЕ
                        battle_ui.set_popup_buttons(
                            action_buttons,
                            outline_colors=None,
                            layout='horizontal',
                            padding=5
                        )
                        battle_ui.set_message("Выбери тип атаки:")
                        current_state = STATE_ACTION
                    elif result == 2:  # ПРЕДМЕТЫ
                        # Не восстанавливаем HP, только сообщение
                        battle_ui.set_message("У тебя нет предметов.  (Нажми Enter)")
                        current_state = STATE_RESULT_SHOW
                    elif result == 3:  # ДУМАТЬ
                        # Не меняем HP, только сообщение
                        battle_ui.set_message("Хмм... может, лучше атаковать?  (Нажми Enter)")
                        current_state = STATE_RESULT_SHOW

                elif current_state == STATE_ACTION and result >= 1000:
                    popup_index = result - 1000
                    chosen = action_buttons[popup_index]
                    if chosen == "НАЗАД":
                        battle_ui.clear_popup_buttons()
                        battle_ui.restore_initial()
                        current_state = STATE_MAIN
                    else:
                        result_text = action_results[chosen] + "  (Нажми Enter)"
                        battle_ui.set_message(result_text)
                        battle_ui.clear_popup_buttons()
                        current_state = STATE_RESULT_SHOW

        if current_state == STATE_SHRINK_HOR:
            elapsed = pg.time.get_ticks() - shrink_start_time
            progress = min(elapsed / shrink_duration, 1.0)

            new_width = original_width - (original_width - shrink_target_width) * progress
            battle_ui.text_area_rect.width = new_width
            battle_ui.text_area_rect.centerx = original_center_x

            new_y = original_buttons_y + (target_buttons_y - original_buttons_y) * progress
            battle_ui.set_main_buttons_y(new_y)

            if progress >= 1.0:
                current_state = STATE_BATTLE
                mini_game = BattleMiniGame(battle_ui, battle_ui.text_area_rect.copy(), 
                           enemy_damage=3, damage_interval=250) #ТУТ УРОН ЕСЛИ ЧТО И МИЛИСЕКУНДЫ УКАЗЫВАЮТСЯ 

        if current_state == STATE_BATTLE and mini_game:
            mini_game.update()
            if mini_game.is_finished():
                battle_ui.text_area_rect = original_text_rect.copy()
                battle_ui.set_main_buttons_y(original_buttons_y)
                battle_ui.clear_popup_buttons()
                battle_ui.enable_input()
                if mini_game.is_victory():
                    battle_ui.set_message("Ты продержался 10 секунд! Бой окончен.")
                else:
                    battle_ui.set_message("Ты погиб или прервал бой.")
                current_state = STATE_MAIN
                mini_game = None

        battle_ui.draw()
        if current_state == STATE_BATTLE and mini_game:
            mini_game.draw(screen)

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()