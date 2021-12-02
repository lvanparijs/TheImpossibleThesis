from random import randint
import os

import pygame

from src.Camera import Camera
from src.Game import Game
from src.Level import Level
from src.Particle import Particle
from src.Platform import Platform
from src.Player import Player

SCR_W = 640
SCR_H = 480

FPS = 60

COLOUR1 = (1, 53, 61, 255)
COLOUR2 = (52, 157, 172, 255)
COLOUR_TEXT = (255, 255, 255)
COLOUR_TEXT_INV = (0, 0, 0)

vec = pygame.math.Vector2

# Game Fonts
font = "src/res/futureforces.ttf"


# Text Renderer
def text_format(message, textFont, textSize, textColor):
    newFont = pygame.font.Font(textFont, textSize)
    newText = newFont.render(message, True, textColor)

    return newText


def vertical_gradient(size, startcolor, endcolor):
    """
    Draws a vertical linear gradient filling the entire surface. Returns a
    surface filled with the gradient (numeric is only 2-3 times faster).
    """
    height = size[1]
    bigSurf = pygame.Surface((1, height)).convert_alpha()
    dd = 1.0 / height
    sr, sg, sb, sa = startcolor
    er, eg, eb, ea = endcolor

    rm = (er - sr) * dd
    gm = (eg - sg) * dd
    bm = (eb - sb) * dd
    am = (ea - sa) * dd

    for y in range(height):
        bigSurf.set_at((0, y), (int(sr + rm * y), int(sg + gm * y), int(sb + bm * y), int(sa + am * y)))
    return pygame.transform.scale(bigSurf, size)


def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect  # l = left,  t = top
    _, _, w, h = camera  # w = width, h = height
    return pygame.Rect(-l + SCR_W / 6, -t + SCR_H / 2, w, h)


def complex_camera(camera, target_rect):
    # we want to center target_rect
    x = -target_rect.center[0] + SCR_W / 6
    y = -target_rect.center[1] + SCR_H / 2
    # move the camera. Let's use some vectors so we can easily substract/multiply
    camera.topleft += (pygame.Vector2((x, y)) - pygame.Vector2(camera.topleft)) * 0.06  # add some smoothness coolnes
    # set max/min x/y so we don't see stuff outside the world
    camera.x = max(-(camera.width - SCR_W), min(0, camera.x))
    camera.y = max(-(camera.height - SCR_H), min(0, camera.y))

    return camera


class Main():

    def __init__(self):
        # Display variables
        pygame.init()  # Initialise display

        self.chosen_level = ''

        (self.screen_width, self.screen_height) = (SCR_W, SCR_H)  # Set screen size

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        pygame.display.set_caption('The Impossible Game')  # Set Title
        pygame.display.set_icon(pygame.image.load("src/res/player.png"))  # Set Game Icon

        # Game variables
        self.clock = pygame.time.Clock()  # Initialise game clock
        self.camera = Camera(complex_camera, self.screen_width, self.screen_height)

        self.gradient = vertical_gradient((SCR_W, SCR_H), COLOUR1, COLOUR2)
        self.main_menu()

    def main_menu(self):
        particles = []

        selected = "start"
        tmp_player = Player((0,276))
        tmp_player.rotate = True

        ground_height = int(self.screen_height * 0.66)

        entities = pygame.sprite.Group()
        entities.add(Platform(vec(0, ground_height), self.screen_width))

        start = False
        lvl = Level(None, SCR_H, tmp_player, [], self.screen_height*0.9,[])

        explosion = False
        explosion_cnt = 40
        cnt = 0

        title1 = text_format("The", font, 100, COLOUR_TEXT)
        title2 = text_format("Impossible", font, 100, COLOUR_TEXT)
        title3 = text_format("Game", font, 100, COLOUR_TEXT)

        t1_alpha = 255
        t1_lo = 0  # randint(0, 255)
        t1_hi = 255  # randint(t1_lo, 255)
        t1_sign = 1

        t2_alpha = 155
        t2_lo = 155
        t2_hi = 255
        t2_sign = 1

        t3_alpha = 55
        t3_lo = 0  # randint(0, 255)
        t3_hi = 255  # randint(t3_lo, 255)
        t3_sign = 1

        title1_rect = title1.get_rect()
        title2_rect = title2.get_rect()
        title3_rect = title3.get_rect()

        selected_ind = 0
        selected = ['level','tutorial','quit']

        tutorial = False #Flag for whether or not to play the tutorial

        lvl_ind = 0
        lvls = self.get_all_levels()

        prefix = 'src/lvl/'
        suffix = '.obj'

        print(lvls)
        sel_level_name = lvls[lvl_ind]

        if prefix in sel_level_name:
            sel_level_name = sel_level_name.replace(prefix, '')
        if suffix in sel_level_name:
            sel_level_name = sel_level_name.replace(suffix, '')
        self.chosen_level = sel_level_name

        while not start:
            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))

            # Main Menu UI
            if selected[selected_ind] == "level":
                text_start = text_format("<"+sel_level_name+">", font, 80, COLOUR_TEXT)
            else:
                text_start = text_format(sel_level_name, font, 80, COLOUR_TEXT_INV)
            if selected[selected_ind] == "quit":
                text_quit = text_format("<QUIT>", font, 80, COLOUR_TEXT)
            else:
                text_quit = text_format("QUIT", font, 80, COLOUR_TEXT_INV)
            explanation = text_format("UP/DOWN = CHOOSE \t \t SELECT = ENTER", font, 30,
                                      COLOUR_TEXT)
            if selected[selected_ind] == "tutorial":
                text_tutorial = text_format("<TUTORIAL>", font, 80, COLOUR_TEXT)
            else:
                text_tutorial = text_format("TUTORIAL", font, 80, COLOUR_TEXT_INV)

            start_rect = text_start.get_rect()
            quit_rect = text_quit.get_rect()
            tutorial_rect = text_tutorial.get_rect()
            expl_rect = explanation.get_rect()

            if t1_alpha >= t1_hi:
                t1_sign = -1
            elif t1_alpha <= t1_lo:
                t1_sign = 1
            t1_alpha += t1_sign

            title1.set_alpha(t1_alpha)

            if t2_alpha >= t2_hi:
                t2_sign = -1
            elif t2_alpha <= t2_lo:
                t2_sign = 1

            t2_alpha += t2_sign
            title2.set_alpha(t2_alpha)

            if t3_alpha >= t3_hi:
                t3_sign = -1
            elif t3_alpha <= t3_lo:
                t3_sign = 1

            t3_alpha += t3_sign
            title3.set_alpha(t3_alpha)

            # Main Menu Text
            entities.draw(self.screen)

            self.screen.blit(title1, (20, 20))
            self.screen.blit(title3, (355, 140))
            self.screen.blit(text_start, (self.screen_width / 2 - (start_rect[2] / 2), 260))
            self.screen.blit(text_tutorial, (self.screen_width / 2 - (tutorial_rect[2] / 2), 330))
            self.screen.blit(text_quit, (self.screen_width / 2 - (quit_rect[2] / 2), 400))

            tmp_player.draw(self.screen, self.camera)
            self.screen.blit(title2, (self.screen_width / 2 - (title2_rect[2] / 2), 80))
            cnt += 1
            if cnt < explosion_cnt:
                self.mini_explosion(particles)
            else:
                explosion_cnt = randint(30, 50)
                cnt = 0
                loc = tmp_player.rect.topright
                particles = []
                for i in range(1, 70):
                    particles += [Particle(loc)]

            self.screen.blit(explanation, (20, 450))

            pygame.display.update()
            self.clock.tick(FPS)

            tmp_player.jump(entities)
            tmp_player.move(lvl.width)
            tmp_player.update(lvl)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_ind -= 1
                        selected_ind = max(0,selected_ind)
                    elif event.key == pygame.K_DOWN:
                        selected_ind += 1
                        selected_ind = min(len(selected)-1, selected_ind)
                    print(selected[selected_ind])
                    if event.key == pygame.K_RETURN:
                        if selected[selected_ind] == "level":
                            start = True
                            self.explosion(tmp_player, lvl)
                            print("Start")
                        if selected[selected_ind] == "quit":
                            pygame.quit()
                            quit()
                    if event.key == pygame.K_LEFT and selected[selected_ind] == "level":
                        lvl_ind -= 1
                        lvl_ind = max(0,lvl_ind)
                        sel_level_name = lvls[lvl_ind]
                        if prefix in sel_level_name:
                            sel_level_name = sel_level_name.replace(prefix, '')
                        if suffix in sel_level_name:
                            sel_level_name = sel_level_name.replace(suffix, '')
                        self.chosen_level = sel_level_name
                    elif event.key == pygame.K_RIGHT and selected[selected_ind] == "level":
                        lvl_ind += 1
                        lvl_ind = min(len(lvls)-1, lvl_ind)
                        sel_level_name = lvls[lvl_ind]
                        if prefix in sel_level_name:
                            sel_level_name = sel_level_name.replace(prefix, '')
                        if suffix in sel_level_name:
                            sel_level_name = sel_level_name.replace(suffix, '')
                        self.chosen_level = sel_level_name



        self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
        pygame.display.update()

    def mini_explosion(self, particles):
        if len(particles) > 0:
            for p in particles:  # Particle check
                if p.get_alpha() <= 0:
                    particles.remove(p)
                else:
                    p.update()
                    p.draw(self.screen, self.camera)
            return False
        else:
            return True

    def explosion(self, player, lvl):
        pos = player.rect.center
        # Explosion animation, purely for aesthetics
        particles = []
        for i in range(1, 100):
            particles += [Particle(pos)]

        while len(particles) > 0:  # Run until all particles faded

            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            obs = lvl.get_all_obstacles(self.camera.state.topleft[0],self.camera.state.topright[0])
            for entity in obs:
                self.screen.blit(entity.surf, self.camera.apply(entity.rect))
            for p in particles:  # Particle check
                if p.get_alpha() <= 0:
                    particles.remove(p)
                else:
                    p.update()
                    p.draw(self.screen, self.camera)
            pygame.display.update()
            self.clock.tick(FPS)
        self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
        pygame.display.update()

    def get_all_levels(self):
        path = 'src/lvl/'
        list_of_files = []

        for root, dirs, files in os.walk(path):
            for file in files:
                list_of_files.append(os.path.join(root, file))
        for name in list_of_files:
            print(name)
        return list_of_files

main = Main()
game = 1
restart = True
START_POS = (40,370)
player = Player(START_POS)

while True:
    if not restart:
        main = Main()
        restart = True
    else:
        main.get_all_levels()
        player.reset(START_POS)
        print(main.chosen_level)
        game = Game(main.chosen_level,player, main.screen, SCR_W, SCR_H)
        restart = game.restart
        game = None


