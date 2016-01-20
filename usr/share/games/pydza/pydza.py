# -*- coding: cp1252 -*-

import pygame
from pygame.locals import *
from random import *
from funcs import *
from menus import *

#constantes
SCREENRECT = Rect(0, 0, 640, 480)
PERSO_SPEED = 5
JUMPZ = 128

# game vars.
#level_file = ""
game_running = 0
#Score au début du jeu :P
score = 0
#Nombre de vie au début du jeu
lives = 3
#Nombre maximum de vies
maxlives = 5

class Actor(pygame.sprite.Sprite):
    """Parent de tous les types de sprites."""
    def __init__(self, posX, posY):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.left = posX
        self.rect.top = posY

    def touch(self, other):
        """Fonction appelée quand un actor en touche un autre.
        Détermine de quel coté on touche et appelle la fonction
        correspondate."""

        # On vérifie que ce qui touche est toujours "vivant" (sinon on peut mourir deux fois avec les Pikes)
        if not other.alive() or (isinstance(other, Player) and other.dying):
            return

        b_dist = abs(self.rect.bottom - other.rect.top)
        t_dist = abs(self.rect.top - other.rect.bottom)
        r_dist = abs(self.rect.right - other.rect.left)
        l_dist = abs(self.rect.left - other.rect.right)

        if b_dist < t_dist:
            huh = "b"
            dist = b_dist
        else:
            huh = "t"
            dist = t_dist
        if l_dist == dist or r_dist == dist:
            return
        if l_dist < dist:
            huh = "l"
            dist = l_dist
        if r_dist < dist:
            huh = "r"

        if huh == "t":
            self.top_touch(other)
        elif huh == "b":
            self.bottom_touch(other)
        else:
            self.side_touch(other, huh == "l")

    def top_touch(self, other):
        pass

    def bottom_touch(self, other):
        pass

    def side_touch(self, other, side):
        pass

class Deco(Actor):
    def __init__(self, posX, posY, *images):
        self.image = load_image(images[0])
        self.animated = len(images) > 1
        if self.animated:
            self.images = []
            for im in images:
                self.images.append(load_image(im))
            self.frame = 0
        Actor.__init__(self, posX, posY)

    def update(self):
        if self.animated:
            self.frame += 1
            self.image = self.images[self.frame/5%len(self.images)]

def gen_bricks(b_class, posX, posY, image, nbX = 1, nbY = 1):
    """Crée un "mur" de nbX x nbY "briques" à partir du
    point (posX,posY)."""
    isx = image.get_width()
    isy = image.get_height()
    for x in range(0, nbX):
        for y in range(0, nbY):
            b_class(posX+(isx*x), posY+(isy*y), image)

class Brick(Actor):
    """Sprite utilisé pour faire des plateformes sur lesquelles
    on peut marcher"""
    def __init__(self, posX, posY, image):
        self.image = image
        Actor.__init__(self, posX, posY)

class WeakBrick(Brick):
    """Hey, je tombe."""
    def __init__(self, posX, posY, image):
        Brick.__init__(self, posX, posY, image)
        self.images = [image, load_image('blank.gif')]
        self.frame = 0
        self.touched = 0
        self.respawning = 0
        self.origY = posY

    def update(self):
        Brick.update(self)
        if self.respawning:
            self.timetospawn -= 1
            if self.timetospawn <= 0:
                self.respawning = 0
                self.image = self.images[0]
                self.rect.top = self.origY
                self.frame = 0
        if self.touched:
            self.frame += 1
            self.image = self.images[self.frame/2%2]
            if self.frame == 20:
                self.hide()
                self.touched = 0

    def top_touch(self, other):
        if not self.respawning:
            self.touched = 1

    def bottom_touch(self, other):
        if not self.respawning:
            self.hide()

    def hide(self):
        self.rect = Rect(self.rect.left,999,self.rect.width,self.rect.height)
        self.image = self.images[1]
        self.timetospawn = 100
        self.respawning = 1

class Pike(Brick):
    """Malheuresement, le joueur n'est pas un fakir."""
    def top_touch(self, other):
        if isinstance(other, Player):
            other.die()

class MadBrick(Pike):
    def bottom_touch(self, other):
        self.top_touch(other)

    def side_touch(self, other, side):
        self.top_touch(other)

class Mover(Brick):
    """Ca s'en va et ça revient..."""
    def __init__(self, posX, posY, image, maxH=100):
        Brick.__init__(self, posX, posY, image)
        self.ported = None
        self.maxheight = maxH
        self.height = 0
        self.direction = 1

    def update(self):
        self.rect.move_ip(0, self.direction)
        self.height += self.direction
        if self.ported != None:
            self.ported.rect.move_ip(0, self.direction)
        if self.height >= self.maxheight or self.height <= 0:
            self.direction = -self.direction
        self.ported = None

    def top_touch(self, other):
        self.ported = other

class Life(Actor):
    """Same player shoots again."""
    image = load_image('heart1.gif')
    touchsound = load_sound('1up.wav')

    def touch(self):
        global lives
        self.touchsound.play()
        if lives < maxlives:
            lives += 1

class Pizza(Actor):
    """Des points, collect most of them to get extra lives."""
    images = load_images('piz1.gif','piz2.gif','piz3.gif','piz4.gif','piz5.gif',
        'piz6.gif','piz7.gif','piz8.gif','piz9.gif')
    for x in range(0,7):
        images.append(images[7-x])
    image = images[0]
    animcycles = 5
    frame = 0
    pickupsound = load_sound('coin.wav')

    def update(self):
        self.frame += 1
        self.image = self.images[self.frame/self.animcycles%16]

    def touch(self):
        global lives, score
        score += 1
        self.pickupsound.play()
        if score%50 == 0 and lives < maxlives:
            lives += 1

class Pizzaman(Actor):
    """ Acteur de fin de niveau.
    Peu très bien servir comme déco aussi x)"""
    image = load_image('pizzaman.gif')
    touchsound = load_sound('youpi.wav')

class Waddledee(Actor):
    """AAH ! Un méchant !"""
    def __init__(self, posX, posY, startdir = 1):
        # Images...
        self.init_images()
        Actor.__init__(self, posX, posY)
        # Son
        self.diesound = load_sound('bounce.wav')
        # Animation
        self.frame = 0
        self.animcycles = 5
        # Déplacement
        self.falling = 1
        self.direction = startdir
        self.speed = 1

    def init_images(self):
        self.images = load_images('waddledee1.gif', 'waddledee2.gif', 'waddledee3.gif', 'waddledee4.gif')
        for x in range(0,4):
            self.images.append(pygame.transform.flip(self.images[x], 1, 0))
        self.image = self.images[0]

    def update(self):
        # Se déplace de gauche à droite et vice (et) versa et tombe si doit tomber
        self.rect.move_ip(self.speed*self.direction, 2*self.falling)
        self.falling = 1
        self.frame += 1
        frame = self.frame/self.animcycles%4
        if self.direction == -1:
            frame += 4
        self.image = self.images[frame]
        # Sortie d'écran ?
        if self.rect.top >= SCREENRECT.bottom:
            self.kill() # Le truc est tombé hors de l'écran, on le tue.

    def top_touch(self, other):
        # Aïe ma tête, on fait rebondir ce qui m'a tapé
        if isinstance(other, Player):
            other.falling = 0
            other.jumping = 1
            other.jump_height = 0
        # Et ensuite je meurs
        Poof(self)
        self.diesound.play()
        self.kill()

    def bottom_touch(self, other):
        self.falling = 0
        # On se met bien au niveau du sol.
        self.rect.bottom = other.rect.top + 1

    def side_touch(self, other, side):
        # Mwahaha pauvre joueur
        if isinstance(other, Player):
            other.die()
        # Oh un mur, je fais demi-tour
        else:
            self.direction = -self.direction

class Togezo(Waddledee):
    """AAAH ! Un autre méchant encore plus méchant !"""
    def init_images(self):
        self.images = load_images('togezo1.gif','togezo2.gif','togezo3.gif','togezo4.gif')
        for x in range(0,4):
            self.images.append(pygame.transform.flip(self.images[x], 1, 0))
        self.image = self.images[0]

    def top_touch(self, other):
        self.side_touch(other, 0)

class Dafly(Waddledee):
    def __init__(self, posX, posY, startdir = 1):
        Waddledee.__init__(self, posX, posY, startdir)
        self.speed = 2

    def init_images(self):
        self.images = load_images('dafly1.gif','dafly2.gif','dafly3.gif')
        self.images.append(self.images[1])
        for x in range(0,4):
            self.images.append(pygame.transform.flip(self.images[x], 1, 0))
        self.image = self.images[0]

    def update(self):
        self.falling = 0
        Waddledee.update(self)

    def bottom_touch(self, other):
        self.side_touch(other, 0)

class Nuage(Actor):
    """Un peu de déco dans le ciel..."""
    def __init__(self, lvl_begin):
        self.image = load_image('nuage.gif')
        if lvl_begin:
            maxX = get_level_size(current_level)
        else:
            maxX = get_level_size(current_level)+GAMERECT.left
        minX = 640*(not lvl_begin)
        posX = randint(minX, max(minX,maxX))
        posY = randint(0, 256)
        Actor.__init__(self, posX, posY)
        self.speedmodif = randint(1, 5)
        self.cycle = 0

    def update(self):
        self.cycle += 1
        if self.cycle % self.speedmodif == 0:
            self.rect.move_ip(-1, 0)
        if self.rect.right <= GAMERECT.left:
            Nuage(0) # Des nuages... toujours des nuages...
            self.kill()

class Poof(Actor):
    """Espèce d'explosion bizarre."""
    def __init__(self, owner):
        self.images = load_images('poof1.gif','poof2.gif','poof3.gif','poof4.gif')
        self.image = self.images[0]
        Actor.__init__(self, owner.rect.left, owner.rect.top)
        self.frame = 0
        self.animcycles = 5

    def update(self):
        self.frame += 1
        frame = self.frame/self.animcycles%4
        self.image = self.images[frame]
        if frame == 3:
            self.kill()

class Trigger(Actor):
    image = load_image('blankline.gif')
    def __init__(self, posX, *event):
        Actor.__init__(self, posX, -160)
        self.event = event

    def trigger(self):
        line = str(self.event[0]) + "("
        bFoundPosX = 0
        for x in range(1, len(self.event)):
            if x > 1:
                line = line + ","
            if(not bFoundPosX and (type(self.event[x]) == int)):
                word = str(self.event[x]+GAMERECT.left)
                bFoundPosX = 1
            else:
                word = str(self.event[x])
            line = line + word
        line = line + ")"
        spawned = eval(line)
        spawned.triggered = 1
#-------------------------------------------------------
# HUD
class HUD(pygame.sprite.OrderedUpdates):
    def __init__(self):
        pygame.sprite.OrderedUpdates.__init__(self)
        Heart.containers = self
        HUDPizza.containers = self
        PizzaNum.containers = self
        LevelNum.containers = self
        for x in range(0, maxlives):
            h = Heart(x)
        HUDPizza()
        PizzaNum()
        LevelNum()

class Heart(pygame.sprite.Sprite):
    def __init__(self, num):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.lifeimg = load_images('heart1.gif','heart2.gif')
        self.image = self.lifeimg[0]
        self.rect = self.image.get_rect()
        self.rect.left = 8+(self.rect.width+2)*num
        self.rect.top = 8
        self.num = num

    def update(self):
        self.image = self.lifeimg[lives <= self.num]

class HUDPizza(pygame.sprite.Sprite):
    images = Pizza.images
    image = images[0]
    animcycles = 5
    frame = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.left = 8
        self.rect.top = 32

    def update(self):
        self.frame += 1
        self.image = self.images[self.frame/self.animcycles%16]

class PizzaNum(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = load_font('freesansbold.ttf', 12)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect()
        self.rect.left = 38
        self.rect.top = 34

    def update(self):
        if score != self.lastscore:
            self.lastscore = score
            msg = "%d" % score
            self.image = self.font.render(msg, 0, self.color)

class LevelNum(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = load_font(level_font,15)
        self.color = (246,180,53)
        self.lastlevel = -1
        self.update()
        self.rect = self.image.get_rect()
        self.rect.left = 100
        self.rect.top = 7

    def update(self):
        if(current_level != self.lastlevel):
            self.lastlevel = current_level
            msg = level_txt + str(current_level+1)
            self.image = self.font.render(msg, 1, self.color)

# Joueur
def directional_image(imlist, dir):
    if dir == 1:
        return imlist[0]
    else:
        return imlist[1]

class Player(Actor):
    """Personnage joueur"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        # Chargement et initialisation de tous les sprites
        self.images = load_images('player_run1.gif','player_run2.gif','player_run3.gif')
        for x in range(0, 3):
            self.images.append(pygame.transform.flip(self.images[x], 1, 0))
        img = load_image('player_jumping.gif')
        self.jumpimage = [img, pygame.transform.flip(img, 1, 0)]
        img = load_image('player_falling.gif')
        self.fallimage = [img, pygame.transform.flip(img, 1, 0)]
        img = load_image('player_stand1.gif')
        self.standimage = [img, pygame.transform.flip(img, 1, 0)]
        self.deadimage = load_image('player_dead.gif')
        self.image = self.standimage[0]
        self.frame = 0
        self.animcycles = 3
        # Sons
        self.jumpsound = load_sound('jump.wav')
        self.diesound = load_sound('dead.wav')
        # Positionnement
        self.rect = self.image.get_rect()
        self.rect.centerx = 20
        self.rect.bottom = 400
        # Variables de mouvement
        self.jumping = 0
        self.holdjump = 0
        self.jump_height = 0
        self.falling = 1
        self.direction = 1 # Surtout uilisé pour les animations.
        self.cant_move = 0 # 0: état normal, 1: ne peut aller à droite, -1: ne peut aller à gauche
        self.walldodge = 0 # 0: rien, 1: walldodge à droite, -1: walldodge à gauche
        self.dying = 0
        self.dietime = 0

    def jump(self):
        if self.dying:
            return
        if not self.jumping and not self.falling:
            self.jumping = 1
            self.jumpsound.play()
        elif self.cant_move != 0:
            self.jumping = 1
            self.jump_height = 0
            self.falling = 0 # au cas ou...
            self.walldodge = -self.cant_move
            self.jumpsound.play()

    def update(self):
        if self.dying:
            self.update_dying()
            return

        self.cant_move = 0
        # gestion des sauts
        if self.jumping:
            # Si on a pas encore atteint la hauteur maxi
            if self.jump_height < JUMPZ:
                # On monte...
                self.rect.move_ip(0, -PERSO_SPEED)
                self.jump_height = self.jump_height + PERSO_SPEED
                self.image = directional_image(self.jumpimage, self.direction)
                if self.jump_height >= JUMPZ/2:
                    self.walldodge = 0
            else:
                # Sinon bah il faut descendre xD
                self.jumping = 0
                self.falling = 1
                self.jump_height = 0
        elif self.falling and not self.jumping:
            # Alors on descend
            self.rect.move_ip(0, PERSO_SPEED)
            self.image = directional_image(self.fallimage, self.direction)
        self.falling = 1
        # Sortie d'écran ?
        if self.rect.top >= SCREENRECT.bottom:
            self.die() # Le joueur est tombé hors de l'écran, on le tue.

    def update_dying(self):
        self.rect.move_ip(0, -1)
        self.dietime += 1
        if self.dietime >= 128:
            if lives == 0:
                game_over()
                return
            # on renvoie tous les sprites à leur position initiale (si ça a scrollé)
            for spr in all.sprites():
                spr.rect.move_ip(-GAMERECT.left, 0)
            GAMERECT.move_ip(-GAMERECT.left, 0)
            # On remet les ennemis (pas de ennemies.empty() parce qu ça ne fonctionne que sur le 1er niveau)
            for enn in ennemies.sprites():
                enn.kill()
            for trig in triggers.sprites():
                trig.kill()
            for s in all.sprites():
                if hasattr(s, "triggered"):
                    s.kill()
            load_ennemies(current_level)
            # On remet le perso...
            self.kill()
        
    def move(pawn, others, dir, run=0):
        if pawn.dying:
            return
        if dir != pawn.cant_move:
            # C'est le player qui bouge s'il n'est pas au centre de l'écran, si il va en arrière ou si on est arrivé au bout du niveau
            if (abs(pawn.rect.centerx - SCREENRECT.centerx) > PERSO_SPEED and (GAMERECT.right <= SCREENRECT.right or GAMERECT.left >= SCREENRECT.left)) or \
                (GAMERECT.right <= SCREENRECT.right and dir == 1) or \
                (GAMERECT.left >= SCREENRECT.left and dir == -1):
                pawn.rect.move_ip(dir*PERSO_SPEED*(1+run), 0)
                # On empèche le player de sortir de l'écran par les cotés
                pawn.rect.clamp_ip(0,-128,640,672) # Top négatif pour permettre au joueur d'avancer plus haut que l'écran
            # Sinon c'est le niveau qui se déplace.
            else:
                for truc in others.sprites():
                    truc.rect.move_ip(-dir*PERSO_SPEED*(1+run), 0)
                GAMERECT.move_ip(-dir*PERSO_SPEED*(1+run), 0)
        # Mise à jour des animations
        if dir != 0:
            pawn.direction = dir
        if not(pawn.jumping or pawn.falling):
            if dir != 0:
                pawn.frame += 1
                pawn.image = pawn.images[0]
                frame = pawn.frame/pawn.animcycles%3
                if dir == -1:
                    frame += 3
                pawn.image = pawn.images[frame]
            else:
                pawn.image = directional_image(pawn.standimage, pawn.direction)

    def die(self):
        global lives
        if self.dying:
            return
        # On perd une vie
        lives = lives - 1
        #self.kill()
        self.dying = 1
        self.image = self.deadimage
        self.diesound.play()

    def touch(self, other):
        if not self.dying:
            Actor.touch(self, other)

    def top_touch(self, other):
        self.jumping = 0
        self.walldodge = 0

    def bottom_touch(self, other):
        self.falling = 0
        self.jump_height = 0
        # On se met bien au niveau du sol.
        self.rect.bottom = other.rect.top + 1

    def side_touch(self, other, side):
        if side == 1:
            self.cant_move = -1
            # on empèce de passer au travers des murs.
            self.rect.left = other.rect.right - 1 # -1 sinon il peut avoir Parkinson
        else:
            self.cant_move = 1
            self.rect.right = other.rect.left + 1

def game_over():
    global game_running
    game_running = 0
    load_sound('gameover.wav').play()
    #main_menu()

def end_level():
    global GAMERECT, current_level, txt_niveau, level_file
    from funcs import screen, background
    # On vire tout
    bricks.empty()
    pickups.empty()
    ennemies.empty()
    stand.empty()
    triggers.empty()
    allbutplayer.empty()
    all.empty()
    nuages.empty()

    current_level += 1
    level_file = ""

    # et on charge le niveau suivant.
    load_level(current_level)
    
    if game_running:
        load_ennemies(current_level)
        GAMERECT = Rect(0 , 0, get_level_size(current_level), 480)
        draw_levelnum(current_level, level_author)
    
def end_game():
    global game_running
    game_running = 0
    load_sound('poussin.wav').play()

def restart_level():
    global current_level, lives

    current_level -= 1
    end_level()

def run():
    """Programme principal"""

    global current_level, game_running, lives, maxlives, score, GAMERECT, txt_niveau
    global bricks, pickups, ennemies, stand, allbutplayer, all, nuages, triggers, level_file

    draw_background()
    from funcs import screen, background, clock

    # groupes de sprites
    bricks = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    ennemies = pygame.sprite.Group()
    stand = pygame.sprite.GroupSingle()
    nuages = pygame.sprite.RenderUpdates()
    allbutplayer = pygame.sprite.Group()
    all = pygame.sprite.OrderedUpdates()
    triggers = pygame.sprite.Group()
	
    Nuage.containers = nuages, allbutplayer
    Deco.containers = allbutplayer, all
    Waddledee.containers = ennemies, allbutplayer, all
    Pizzaman.containers = stand, allbutplayer, all
    Life.containers = pickups, allbutplayer, all
    Pizza.containers = pickups, allbutplayer, all
    Brick.containers = bricks, allbutplayer, all
    Poof.containers = allbutplayer, all
    Trigger.containers = triggers, allbutplayer
    Player.containers = all

    if level_file == "":
        current_level = 0
    else:
        current_level = 1337
    #-------------------------------------------------
    # Définition du niveau
    #
    # On se remet bien au début du niveau
    load_level()
    load_ennemies()
    GAMERECT = Rect(0 , 0, get_level_size(), 480)
    #-------------------------------------------------

    #clock = pygame.time.Clock() #Gestion du temps.
    #Jeu...
    game_running = 1
    lives = 3
    maxlives = 5
    score = 0

    #création du joueur
    player = Player()
    # et du HUD
    hud = HUD()

    pausesound = load_sound('pause.wav')

    # Affichage du niveau actuel au début du niveau
    #Cet affichage sert uniquement lors du premier lancement du jeu, ensuite il est généré
    #a partir de la fonction end_level
    if level_file == "":
        draw_levelnum(current_level, level_author)
    
    while game_running:
        clock.tick(40)

        pygame.event.pump()
        keystate = pygame.key.get_pressed()
        if keystate[K_ESCAPE]:
            pausesound.play()
            pygame.mixer.music.pause()
            if not mid_game_menu():
                game_running = 0
            pygame.mixer.music.unpause()

        #if keystate[K_RETURN]:
        #    restart_level()
        #    lives = 3

        # Si le perso meurt, on le fait réapparaitre
        if not player.alive():
            player = Player()

        all.clear(screen, background)
        hud.clear(screen, background)
        nuages.clear(screen, background)
        all.update()
        hud.update()
        nuages.update()

        # Est-ce que le joueur touche quelque chose ? (seulement si il est vivant.)
        if player.alive() and not player.dying:
            # Des briques ?
            for wall in pygame.sprite.spritecollide(player, bricks, 0):
                player.touch(wall)
                wall.touch(player)
            # Un objet ?
            for item in pygame.sprite.spritecollide(player, pickups, 1):
                item.touch()
            # Un trigger ?
            for trig in pygame.sprite.spritecollide(player, triggers, 1):
                trig.trigger()
            # La fin du niveau ?
            for end in pygame.sprite.spritecollide(player, stand, 0):
                end.touchsound.play()
                end_level()
            # Ou un ennemi ?
            for enn in pygame.sprite.spritecollide(player, ennemies, 0):
                enn.touch(player)

        # Collision des briques avec les ennemis
        dict = pygame.sprite.groupcollide(ennemies, bricks, 0, 0)
        for enn in dict.keys():
            for wall in dict[enn]:
                enn.touch(wall)
        dict = pygame.sprite.groupcollide(ennemies, ennemies, 0, 0)
        # Collision entre ennemis
        for enn in dict.keys():
            for wall in dict[enn]:
                if wall != enn:
                    enn.touch(wall)

        # On déplace le joueur.
        if player.walldodge != 0:
            direction = player.walldodge
        else:
            direction = keystate[K_RIGHT] - keystate[K_LEFT]
        player.move(allbutplayer, direction, keystate[K_LSHIFT] or keystate[K_RSHIFT])
        jump = keystate[K_UP]
        if jump and not player.holdjump:
            player.jump()
        player.holdjump = jump

        # On affiche tout.
        dirty = nuages.draw(screen) + all.draw(screen) + hud.draw(screen)
        pygame.display.update(dirty)

    level_file = ""
    if main_menu():
        run() # C'est crade mais j'ai la flemme de faire plus proprement.

#-------------------------------------------------------------------------------------
# Niveaux 

def load_level_file(num, type):
    global level_size, level_author
    try:
        if level_file == "":
            fstring = os.path.join('levels', 'level'+str(num)+'.pdz')
        else:
            fstring = level_file
        # on ouvre le fichier .pdz correspondant au niveau.
        f = open(fstring, 'r')

        bFoundAuthor = 0
        bFoundSection = 0
        bError = False
        # parcours du fichier
        for line in f:
            if not bFoundSection:
                bFoundSection = ("["+type+"]") in line
                continue
            if line.startswith('['):
                break

            # pour chaque ligne, on lui enlève le retour chariot, et on la décompose suivant les ':'
            vars = line.rstrip('\n').rstrip('\r').split(':')
            # si la ligne est vide on passe à la suivante.
            if vars[0] == "":
                continue
            # si la ligne commence par 'size', c'est la taille du niveau, on la stock et on passe
            # à la ligne suivante
            if type == 'level' and vars[0] == "size":
                level_size = int(vars[1])
                continue
            # même chose que précedemment mais pour l'auteur du niveau cette fois-ci
            if type == 'level' and vars[0] == "author":
                level_author = vars[1]
                bFoundAuthor = 1
                continue
            # si la ligne commence par un nom de brique, alors la ligne d'évaluation commence par 'gen_bricks('
            # plus le nom de la brique.
            if vars[0] in ("Brick", "WeakBrick", "Pike", "MadBrick"):
                evalline = "gen_bricks(" + vars[0] + ','
                if not vars[3] in globals().keys():
                    eval(compile("global %s" % vars[3], "omg.tmp", "single"))
                    eval(compile("%s = load_image('%s.gif')" % (vars[3], vars[3]), "omg.tmp", "single"))
            # Sinon la ligne d'évaluation commence par le début de la ligne.
            else:
                evalline = vars[0] + "("
            # on colle le reste de la ligne à la ligne d'éval
            for x in range(1, len(vars)):
                if x > 1:
                    evalline = evalline + ','
                evalline = evalline + vars[x]
            evalline = evalline + ")"
            # on "éxecute" la ligne d'évaluation
            try:
                eval(evalline)
            except SyntaxError:
                if not bError:
                    print "Syntax error in", fstring
                    bError = True
                print "\t" + line
        if type == 'level' and not bFoundAuthor:
            level_author = ""
    
    except IOError:
        # Si on arrive pas à ouvrir le fichier du niveau, on considère que le jeu est terminé.
        if type == 'level':
            end_game()

def get_level_size(num=0):
    return level_size
    
def load_level(num=0):
    load_level_file(num, 'level')
    for x in range(get_level_size(num)/250):
        Nuage(1)

def load_ennemies(num = 0):
    load_level_file(num, 'ennemies')

#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    global level_file
    init()
    if len(sys.argv) > 1:
        level_file = sys.argv[1]
        run()
    else:
        level_file = ""
        if main_menu():
            run()
