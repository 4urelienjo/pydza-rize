# -*- coding: cp1252 -*-

import pygame
from pygame.locals import *
import os.path

SCREENRECT = Rect(0, 0, 640, 480)
#police pouyr l'affichage du niveau actuel, au début du niveau et dans le hud durant la partie
level_font = "BD_Cartoon_Shout.ttf"
#Texte avant le numéro de niveau
level_txt = "Level "

# Fonctions en vrac...
def load_image(file):
    """Charge l'image dont le nom est passé en paramètre."""
    file = os.path.join('img', file)
    if not pygame.display.get_init():
        init()
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, '%s: Impossible de charger l\'image "%s"' % (pygame.get_error(), file)
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

def load_font(font_name,size):
    font = pygame.font.Font(font_name,size)
    return font

def make_pause(duration):
    from time import sleep
    sleep(duration)

class SoundGroup:
    sounds = []

    def add(self, snd):
        if isinstance(snd, pygame.mixer.Sound):
            self.sounds.append(snd)
            snd.set_volume(soundvol)
            
    def set_volume(self, vol):
        for snd in self.sounds:
            snd.set_volume(vol)

class dummysound:
    def play(self): pass

def load_sound(file):
    global sndgrp

    if not pygame.display.get_init():
        init()

        if not pygame.mixer: return dummysound()
    file = os.path.join('sound', file)
    try:
        sound = pygame.mixer.Sound(file)
        sndgrp.add(sound)
        return sound
    except pygame.error:
        print 'Warning, unable to load,', file
    return dummysound()

def load_music(file):
    file = os.path.join('sound',file)
    try:
        pygame.mixer.music.load(file)
    except pygame.error:
        print 'Warning, unable to load', file

def play_music():
    try:
        pygame.mixer.music.play(-1)
    except pygame.error:
        print 'Warning, music not loaded'

def init():
    global screen, clock, sndgrp

    if pygame.display.get_init():
        return

    #Initialisation de pygame et de la fenetre.
    pygame.init()
    clock = pygame.time.Clock() #Gestion du temps.
    #On charge la configuration.
    load_config()
    # ...
    screen = pygame.display.set_mode(SCREENRECT.size, fscreen*FULLSCREEN)
    pygame.display.set_caption('Pydza') #titre
    pygame.mouse.set_visible(0)
    #draw_background()
    # Musique !
    load_music('audio.wav')
    pygame.mixer.music.set_volume(musicvol)
    sndgrp = SoundGroup()
    play_music()

def load_config():
    global musicvol, soundvol, fscreen

    conf = None

    try:
        # on ouvre le fichier
        conf = open('pydza.conf')
        # on met son contenu dans 'config'
        config = conf.readlines()
        conf.close()
        print "Loading configuration."
        # on parcourt les lignes qu'on a sorti.
        for str in config:
            # on cherche le '=' et on affecte les variables comme il faut.
            x = str.find("=")
            if x != -1:
                if str[:x] == "fullscreen":
                    fscreen = int(str[x+1:])
                    print "\tfullscreen=" + fscreen.__str__()
                elif str[:x] == "musicvol":
                    musicvol = float(str[x+1:])
                    print "\tmusicvol=" + musicvol.__str__()
                elif str[:x] == "soundvol":
                    soundvol = float(str[x+1:])
                    print "\tsoundvol=" + soundvol.__str__()
    # S'il y a une erreur, c'est que le fichier existe pas
    except IOError:
        print "No configuration file. Using default."
        # alors on le crée et on y met la config par défaut.
        write_config(["fullscreen",0],["musicvol",1.0],["soundvol", 1.0])
        musicvol = 1.0
        soundvol = 1.0
        fscreen = 0

def write_config(*opt):
    print "Writing configuration."
    try:
        # on ouvre le fichier en lecture écriture sans l'effacer.
        conf = open('pydza.conf', 'a+')
        # copie de son contenu.
        config = conf.readlines()
        # pour toutes les options passées en paramètre...
        for o in opt:
            bFound = 0
            # on cherche si elle existe déjà dans le fichier (ou plutot dans son contenu
            # qui a été copié)
            for line in config:
                if line.find(o[0]) != -1:
                    bFound = 1
                    break
            # si c'est le cas...
            if bFound:
                # on  supprime la ligne en question du contenu
                config.remove(line)
                y = line.find('\n')
                # on met à jour cette ligne (à part)
                line = line.replace(line[len(o[0])+1:y], str(o[1]))
                print '\t' + line.replace('\n', '')
                # et on la réajoute au contenu
                config.append(line)
            # si l'option courante n'est pas dans le contenu
            else:
                # on l'ajoute au contenu.
                config.append(o[0] + "=" + str(o[1]) + "\n")
                print '\t' + config[-1].replace('\n', '')
    
        # on se met au début du fichier
        conf.seek(0)
        # on  l'efface
        conf.truncate()
        # on y écrit le contenu
        conf.writelines(config)
        # et on le ferme
        conf.close()
    except IOError:
        print "Warning: Can't write configuration file."

bgdtile = load_image('horizon.jpg')

def draw_background():
    global screen, background

    # Affichage du fond
    background = pygame.Surface(SCREENRECT.size)
    background.blit(bgdtile, (0,0))
    screen.blit(background, (0,0))
    pygame.display.flip()

def draw_levelnum(num, author):
    draw_background()

    police = load_font(level_font,30)
    text = level_txt+str(num+1)
    surf_text = police.render(text, True,(246,180,53))
    dirty = [screen.blit(surf_text,(230,235))]

    if author != "":
        police = load_font(level_font,15)
        text = "by %s" % author
        surf_text = police.render(text, True,(246,180,53))
        dirty.append(screen.blit(surf_text,(480, 448)))

    #On affiche le texte
    pygame.display.update(dirty)
    make_pause(2)

    draw_background()
