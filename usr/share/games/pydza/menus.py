# -*- coding: cp1252 -*-

import pygame
from pygame.locals import *
from funcs import *
from sys import exit

holding = 0

menusnd = load_sound('menuSound.wav')

def main_menu():
    global holding

    from funcs import screen, clock
    draw_background()

    pygame.mixer.music.unpause()

    dirty = []
    selected = 0

    dirty.append(screen.blit(load_image('logo-iut_orsay.gif'), (8, 430)))
    dirty.append(screen.blit(load_image('logo-python.gif'), (248, 420)))
    dirty.append(screen.blit(load_image('logo-pygame.gif'), (506, 415)))

    startimgs = load_images("menu-startoff.gif", "menu-starton.gif")
    optimgs = load_images("menu-optionsoff.gif", "menu-optionson.gif")
    creditsimgs = load_images("menu-creditsoff.gif", "menu-creditson.gif")
    quitimgs = load_images("menu-quitoff.gif", "menu-quiton.gif")

    while 1:
        clock.tick(40)
        pygame.event.pump()
        keystate = pygame.key.get_pressed()
        if keystate[K_RETURN] and not holding:
            holding = 1
            break
        if not holding and (keystate[K_UP] or keystate[K_DOWN]):
            selected += keystate[K_DOWN] - keystate[K_UP]
            menusnd.play()
        selected %= 4
        holding = keystate[K_UP] or keystate[K_DOWN] or keystate[K_RETURN]

        dirty.append(screen.blit(startimgs[selected == 0], (180, 32)))
        dirty.append(screen.blit(optimgs[selected == 1], (120, 128)))
        dirty.append(screen.blit(creditsimgs[selected == 2], (145, 224)))
        dirty.append(screen.blit(quitimgs[selected == 3], (180, 320)))
        pygame.display.update(dirty)
        dirty = []

    if selected == 0:
        #import pydza
        #pydza.run()
        return True
    elif selected == 1:
        return options_menu()
    elif selected == 2:
        return credits()
    elif selected == 3:
        # Même si ça se coupe tout seul, par principe on éteint la musique.
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.quit() # pareil que la musique, par principe.
        #exit()
        return False

def mid_game_menu():
    global holding
    from funcs import screen, clock
    dirty = []
    selected = 0

    resumeimgs = load_images("menu-resumeon.gif", "menu-resumeoff.gif")
    quitimgs = load_images("menu-quiton.gif", "menu-quitoff.gif")

    while 1:
        clock.tick(40)
        pygame.event.pump()
        keystate = pygame.key.get_pressed()
        if keystate[K_RETURN] and not holding:
            holding = 1
            break
        if not holding and (keystate[K_UP] or keystate[K_DOWN]):
            selected = not selected
            menusnd.play()
        holding = keystate[K_UP] or keystate[K_DOWN] or keystate[K_RETURN]

        dirty.append(screen.blit(resumeimgs[selected], (145, 32)))
        dirty.append(screen.blit(quitimgs[not selected], (180, 128)))
        pygame.display.update(dirty)
        dirty = []

    # On efface ce qui a été affiché
    from funcs import background
    dirty.append(screen.blit(background, (145, 32), (180,32,350,86)))
    dirty.append(screen.blit(background, (180, 128), (180,128,280,86)))
    pygame.display.update(dirty)

    return not selected

def options_menu():
    global holding, fscreen, soundvol

    from funcs import screen, background, clock
    draw_background()

    dirty = []
    selected = 0

    musicvol_text = "Music volume"
    soundvol_text = "Sound volume"
    fullscreen_text = "Full screen"
    back_text = "Back"
    
    vol_bar = load_image('vol_bar.gif')
    button = load_image('button.gif')
    wbutton = load_image('button-off.gif')

    musicvol = 10*pygame.mixer.music.get_volume()
    soundvolume = 10*soundvol
    #fscreen = 0
    newmusic = musicvol
    newsound = soundvolume
    newfscreen = fscreen

    font = pygame.font.Font('freesansbold.ttf', 18)
    dirty.append(screen.blit(load_image('logo-iut_orsay.gif'), (8, 430)))
    dirty.append(screen.blit(load_image('logo-python.gif'), (248, 420)))
    dirty.append(screen.blit(load_image('logo-pygame.gif'), (506, 415)))

    while 1:
        clock.tick(40)
        
        dirty.append(screen.blit(background, (32, 32), (0, 0, 512, 128)))
        
        pygame.event.pump()
        keystate = pygame.key.get_pressed()

        #if keystate[K_ESCAPE]:
        #    break
        if not holding and (keystate[K_UP] or keystate[K_DOWN]):
            selected += keystate[K_DOWN] - keystate[K_UP]
            menusnd.play()
        selected %= 4

        if (keystate[K_LEFT] or keystate[K_RIGHT]) and not holding:
            if selected == 0:
                newmusic += keystate[K_RIGHT] - keystate[K_LEFT]
                if newmusic < 0:
                    newmusic = 0
                if newmusic > 10:
                    newmusic = 10
            elif selected == 1:
                newsound += keystate[K_RIGHT] - keystate[K_LEFT]
                if newsound < 0:
                    newsound = 0
                if newsound > 10:
                    newsound = 10
        elif keystate[K_RETURN] and not holding:
            holding = 1
            if selected == 2:
                newfscreen += 1
                newfscreen %= 2
                # problème avec le fichier de config si on met 'nfs = not nfs'
            elif selected == 3:
                break

        holding = keystate[K_UP] or keystate[K_DOWN] or keystate[K_LEFT] or keystate[K_RIGHT] or keystate[K_RETURN]

        img = font.render(musicvol_text, 1, (255*(selected == 0), 255*(selected == 0), 255))
        dirty.append(screen.blit(img, (32, 32)))
        dirty.append(screen.blit(vol_bar, (192 ,38)))
        dirty.append(screen.blit(button, (184+16*musicvol, 32)))

        img = font.render(soundvol_text, 1, (255*(selected == 1), 255*(selected == 1), 255))
        dirty.append(screen.blit(img, (32, 64)))
        dirty.append(screen.blit(vol_bar, (192 ,72)))
        dirty.append(screen.blit(button, (184+16*soundvolume, 64)))

        img = font.render(fullscreen_text, 1, (255*(selected == 2), 255*(selected == 2), 255))
        dirty.append(screen.blit(img, (32, 96)))
        if fscreen:
            thebutton = button
        else:
            thebutton = wbutton
        dirty.append(screen.blit(thebutton, (184,100)))

        img = font.render(back_text, 1, (255*(selected == 3), 255*(selected == 3), 255))
        dirty.append(screen.blit(img, (32, 128)))

        pygame.display.update(dirty)
        dirty = []
        
        if newmusic != musicvol:
            musicvol = newmusic
            pygame.mixer.music.set_volume(0.1*musicvol)
        if newsound != soundvolume:
            soundvolume = newsound
            sndgrp.set_volume(0.1*soundvolume)
            soundvol = 0.1*soundvolume
        if newfscreen != fscreen:
            fscreen = newfscreen
            pygame.display.set_mode(SCREENRECT.size, FULLSCREEN*fscreen)
            # on redessine tout sinon ça devient (presque) tout noir.
            draw_background()
            dirty.append(screen.blit(load_image('logo-iut_orsay.gif'), (8, 430)))
            dirty.append(screen.blit(load_image('logo-python.gif'), (248, 420)))
            dirty.append(screen.blit(load_image('logo-pygame.gif'), (506, 415)))
            # La souris réapparait quand on repasse en fenêtré
            pygame.mouse.set_visible(0)


    write_config(["fullscreen", fscreen], ["musicvol", musicvol/10], ["soundvol", soundvolume/10])
    return main_menu()

def credits():
    global holding

    from funcs import screen, background, clock
    draw_background()

    dirty = []

    font = load_font('freesansbold.ttf', 16)
    lines = ("Lead programmer: Alban FERON", "Other programmers:", "        Rémy COUTABLE", "        Pierre-Elie MARGUERITTE",
        "Lead 2D designer: Pierre-Elie MARGUERITTE", "Sound:", "        Pierre-Elie MARGUERITTE", "        Alban FERON",
        "Music: Pierre-Elie MARGUERITTE", "Tutor: Eric PETITJEAN",
        "Level designers:", "        Alban FERON", "        Alkazex", "        Duk3Nic0", "        BuBBle",
        "        Skullk", "", "Menu still in construction 8)", "Press ESC")
    for x in range(len(lines)):
        lig = font.render(lines[x], 1, (255, 255, 255))
        dirty.append(screen.blit(lig, (32, 16 + 24*x)))

    pygame.display.update(dirty)
    while 1:
        clock.tick(40)
        pygame.event.pump()
        keystate = pygame.key.get_pressed()
        if keystate[K_ESCAPE]:
            break

    return main_menu()

if __name__ == "__main__":
    print "Please run 'pydza.py'"