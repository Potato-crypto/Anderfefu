from Dvishok.Engine import Engine
from Dvishok.Sprite.Font.Font import Font
from Dvishok.Sprite.Sprite.SpriteSurface import SpriteSurface
from Dvishok import Texture
from Dvishok import Group
from Dvishok.Events.EventType import EventType
from Dvishok.Sprite.Audio.Music import Music
from Dvishok.Sprite.Audio.Sound import Sound
from Dvishok.Sprite.Audio.AudioEngine import AudioEngine
from Dvishok.Clock import Clock


if __name__ == "__main__":
    engine = Engine()
    screen = engine.display.set_mode(1600, 900)
    engine.setup_callback()
    AudioEngine.init()

    font1 = Font("../Dvishok/Assets/fonts/PublicPixel-rv0pA.ttf", 48)
    font2 = Font("../Dvishok/Assets/fonts/PublicPixel-rv0pA.ttf", 30)

    text1 = font1.render(
        "Фуораов крутой текст урааа",
        (0.7, 1.0, 0.7),
        x=200,
        y=300
    )

    text2 = font2.render(
        "абвгдеёжзийклмнопрстуфхцчыьъщшэюя",
        (0.1, 0.5, 0.8),
        x=400,
        y=500
    )

    text3 = font1.render(
        "ПРОЗРАЧНЫЙ TERCNBYF",
        (1.0, 1.0, 1.0, 0.25),
        x=400,
        y=260
    )

    alpha_square1 = SpriteSurface(
        200,
        200,
        engine.get_display().camera,
        color=(255, 0, 0, 128),
        x=500,
        y=200
    )

    alpha_square2 = SpriteSurface(
        200,
        200,
        engine.get_display().camera,
        color=(0, 255, 0, 128),
        x=600,
        y=300
    )

    alpha_texture_square = SpriteSurface(
        400,
        250,
        engine.get_display().camera,
        color=(255, 255, 255, 128),
        texture=Texture("../Dvishok/Assets/images/MainIcon.jpg"),
        x=850,
        y=250
    )

    group = Group(
        text1,
        text2,
        text3,
        alpha_square1,
        alpha_square2,
        alpha_texture_square,
    )

    Music.load("../Dvishok/Assets/audio/your-best-nightmare.mp3")
    Music.set_volume(0.4)
    Music.play(-1)

    ohyes = Sound("../Dvishok/Assets/audio/oh-yes-undertale.mp3")
    ohyes.set_volume(0.7)
    ohyes.play(-1)

    clock = Clock()

    while engine.running:

        # delta_time = clock.tick_seconds(60)

        engine.process_input()

        for event in engine.get_events():

            if event.type == EventType.KEYDOWN:

                if event.dict["name"] == "ESCAPE":
                    engine.stop()

        screen.draw()
        group.draw(screen)

        engine.update()
        clock.tick(60)

    Music.stop()
    ohyes.stop()

    engine.quit()