import math
import sys

from math import cos

import playsound as playsound
import pygame
from pygame import gfxdraw, font, KEYDOWN, K_SPACE, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from src.Camera import Camera
from src.Level import Level
from src.Particle import Particle


# GLOBAL STUFF
vec = pygame.math.Vector2
ENTITY_SIZE = 40
FPS = 60
BG_COLOUR = (52, 157, 172)
NUM_PARTICLES = 250
LVL_W = 2000

ACC = 0.35
FRIC = -0.12
GRAVITY = 0.9
BUFFER = 5
JUMP_VEL = -14

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (50, 50, 50)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

font = "futureforces.ttf"


class Game(pygame.sprite.LayeredUpdates):

    def __init__(self, player, scr, scr_w, scr_h):
        # Display variables
        self.screen = scr
        self.screen_width = scr_w
        self.screen_height = scr_h

        # Game variables
        self.clock = pygame.time.Clock()  # Initialise game clock
        self.score = 0
        self.game_over = False

        self.is_jump = False  # Stores if player is jumping or not

        self.gradient = self.vertical_gradient((self.screen_width, self.screen_height), (1, 53, 61, 255),(52, 157, 172, 255)) #Nice background gradient
        # Update screen
        pygame.display.flip()

        self.player = player
        self.level = None

        scr.blit(self.gradient, pygame.Rect((0, 0, scr_w, scr_h)))
        pygame.display.update()
        self.game_loop()
        self.restart = self.game_over_screen()

    def game_over_screen(self):
        running = True
        lvl = Level(None, self.screen_height, self.player, pygame.sprite.Group(), pygame.sprite.Group(), self.screen_height * 0.9)
        text = self.text_format("GAME OVER", font, 100, white)
        text_menu = self.text_format("Press R to restart \t Press ESC for main menu", font, 20, white)

        alpha = 0
        d_alpha = 1
        while running:

            if alpha <= 0:
                d_alpha = 1
            elif alpha >= 255:
                d_alpha = -1
            alpha += d_alpha
            text.set_alpha(alpha)
            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            self.screen.blit(text, (40, 250))
            self.screen.blit(text_menu, (60, 450))
            lvl.get_all_obstacles(0,self.screen_width).draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        running = False
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        return False

            pygame.display.update()
            self.clock.tick(FPS)

    # Game Loop
    def game_loop(self):
        song_name = 'C:/Users/lvanp/PycharmProjects/TheImpossibleThesis/src/res/trumpet.wav' #Load song
        self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height))) #Paint background
        self.player.attempts += 1 #Increment Attempts

        all_boxes = pygame.sprite.Group() #Initialise boxes
        all_spikes = pygame.sprite.Group() #Initialise Spikes
        self.total_level_height = self.screen_height * 4 #Set Max level height
        l1 = Level(song_name, self.total_level_height, self.player, all_boxes, all_spikes, self.screen_height) #Initialise level
        print("INITIALISE LEVEL")
        #l1.generate_geometry(self.player.max_vel)
        l1.generate_geometry_from_grammar(self.player.max_vel)
        #l1.generate_from_bpm(self.player.max_vel) #Generate Level

        self.camera = Camera(self.complex_camera, l1.width, self.total_level_height) #Initialise camera
        P1 = self.player
        jump = False
        last_jump = []
        jump_adjust_x = 0
        jump_adjust_y = 0
        num_pts = 35
        old_pos_y = 0

        playsound.playsound(song_name, False) #Start sound
        start_time = 0
        jump_cnt = 0
        while not self.game_over:  # Game over check
            cam_rect = self.camera.apply(P1.rect) #Move camera with player
            start_time += 1/FPS #Increment timer

            #Auto jump
            if len(l1.beat_times) > jump_cnt and start_time >= l1.beat_times[jump_cnt]:
                if l1.action_list[jump_cnt]:
                    P1.jump(l1.boxes)
                jump_cnt += 1

            #Manual jump
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        jump = True
                        last_jump = []
                        jump_adjust_x = 0
                        jump_adjust_y = 0
                        old_pos_y = self.camera.state.y
                        for i in range(0, num_pts):
                            last_jump += [vec(cam_rect.centerx,cam_rect.bottom)+P1.sim_jump(i)]
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        jump = False

            if jump:
                jump_cnt += 1
                P1.jump(l1.boxes)
                jump = False

            old_pos_x = P1.pos.x #Change position

            # Update player without checking for collisions
            P1.move(l1.width)

            self.game_over = P1.update(l1) #Update player and collisions
            if self.game_over:
                self.explosion(P1, l1) #Animation


            # Update Camera
            self.camera.update(P1)
            jump_adjust_x += P1.pos.x - old_pos_x
            jump_adjust_y = old_pos_y - self.camera.state.y

            # Draw updates screen
            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            self.draw(l1.get_all_obstacles(P1.pos.x - self.screen_width, P1.pos.x + self.screen_width))

            # DRAW SCORE
            text = self.text_format("ATTEMPT " + str(P1.get_attempts()), font, 60, white)
            self.screen.blit(text, (40, 400))

            #Simulate and draw jump/no_jump
            #pts = []
            #pts_no_jump = []
            #alpha = 255
            #for i in range(0,num_pts):
            #   pts += [P1.sim_jump(i)]
            #   if i < 20:
            #       pts_no_jump += [P1.sim_no_jump(i)]

            #for i in range(1,len(pts)):
            #   alpha -= int(255/num_pts)
            #   self.aaline(self.screen, (0,255,0,alpha) , (cam_rect.centerx+pts[i-1].x,cam_rect.bottom+pts[i-1].y) ,  (cam_rect.centerx+pts[i].x,cam_rect.bottom+pts[i].y),10)
            #   if i < 20:
            #       self.aaline(self.screen, (255, 255, 0, alpha),(cam_rect.centerx + pts_no_jump[i - 1].x, cam_rect.bottom + pts_no_jump[i - 1].y),(cam_rect.centerx + pts_no_jump[i].x, cam_rect.bottom + pts_no_jump[i].y), 10)
            #alpha = 255
            #for i in range(1,len(last_jump)):
            #    alpha -= int(255 / num_pts)
            #    self.aaline(self.screen, (255, 0, 0, alpha),
            #                (last_jump[i - 1].x-jump_adjust_x, last_jump[i - 1].y-jump_adjust_y),
            #                (last_jump[i].x-jump_adjust_x, last_jump[i].y-jump_adjust_y), 10)


            P1.draw(self.screen, self.camera) #Draw player
            pygame.display.update() # Update
            self.clock.tick(FPS)  # Increment clock

    def collision_correction(self, player, lvl):
        hit_left = player.update(lvl)  # Update with box collision
        # Spike collision
        hits_spike = pygame.sprite.spritecollide(player, lvl.get_all_spikes(), False, pygame.sprite.collide_mask)
        if hits_spike or hit_left:
            self.game_over = True
            self.explosion(player, lvl)

    def draw(self, obstacles):
        for entity in obstacles:
            self.screen.blit(entity.surf, self.camera.apply(entity.rect))

    def mini_explosion(self, prtcles):
        if len(prtcles) > 0:
            for p in prtcles:  # Particle check
                if p.get_alpha() <= 0:
                    prtcles.remove(p)
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
        for i in range(1, NUM_PARTICLES):
            particles += [Particle(pos)]

        circle_size = 5
        circle_alpha = 180

        while len(particles) > 0:  # Run until all particles faded

            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))

            self.draw(
                lvl.get_all_obstacles(self.camera.state.topleft[0], self.camera.state.topright[0]))  # Draw obstacles
            circle_size += 2
            circle = pygame.Surface((circle_size * 2, circle_size * 2), pygame.SRCALPHA)
            circle_alpha -= 5
            circle_alpha = max(0, circle_alpha)
            pygame.draw.circle(circle, (255, 255, 0, circle_alpha), (circle_size, circle_size), circle_size)

            self.screen.blit(circle, self.camera.apply(circle.get_rect(center=pos)))

            for p in particles:  # Particle check
                if p.get_alpha() <= 0:
                    particles.remove(p)
                else:
                    p.update()
                    p.draw(self.screen, self.camera)
            pygame.display.update()
            self.clock.tick(FPS)

    def simple_camera(self, camera, target_rect):
        l, t, _, _ = target_rect  # l = left,  t = top
        _, _, w, h = camera  # w = width, h = height
        return pygame.Rect(-l + self.screen_width / 6, -t + self.screen_height / 2, w, h)

    def complex_camera(self, camera, target_rect):
        # we want to center target_rect
        x = -target_rect.center[0] + self.screen_width / 6
        y = -target_rect.center[1] + self.screen_height / 2
        # move the camera. Let's use some vectors so we can easily substract/multiply
        camera.topleft += (pygame.Vector2((x, y)) - pygame.Vector2(
            camera.topleft)) * 0.06  # add some smoothness coolnes
        # set max/min x/y so we don't see stuff outside the world
        camera.x = max(-(camera.width - self.screen_width), min(0, camera.x))
        camera.y = max(-(camera.height - self.screen_height), min(0, camera.y))

        return camera

    # Text Renderer
    def text_format(self, message, textFont, textSize, textColor):
        newFont = pygame.font.Font(textFont, textSize)
        newText = newFont.render(message, True, textColor)

        return newText

    def vertical_gradient(self, size, startcolor, endcolor):
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
            bigSurf.set_at((0, y),
                           (int(sr + rm * y),
                            int(sg + gm * y),
                            int(sb + bm * y),
                            int(sa + am * y))
                           )
        return pygame.transform.scale(bigSurf, size)

    def aaline(self, surface, color, start_pos, end_pos, width=1):
        """ Draws wide transparent anti-aliased lines. """
        # ref https://stackoverflow.com/a/30599392/355230

        x0, y0 = start_pos
        x1, y1 = end_pos
        midpnt_x, midpnt_y = (x0 + x1) / 2, (y0 + y1) / 2  # Center of line segment.
        length = math.hypot(x1 - x0, y1 - y0)
        angle = math.atan2(y0 - y1, x0 - x1)  # Slope of line.
        width2, length2 = width / 2, length / 2
        sin_ang, cos_ang = math.sin(angle), cos(angle)

        width2_sin_ang = width2 * sin_ang
        width2_cos_ang = width2 * cos_ang
        length2_sin_ang = length2 * sin_ang
        length2_cos_ang = length2 * cos_ang

        # Calculate box ends.
        ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
              midpnt_y + width2_cos_ang + length2_sin_ang)
        ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
              midpnt_y + width2_cos_ang - length2_sin_ang)
        bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
              midpnt_y - width2_cos_ang + length2_sin_ang)
        br = (midpnt_x - length2_cos_ang + width2_sin_ang,
              midpnt_y - width2_cos_ang - length2_sin_ang)

        pygame.gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
        pygame.gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)

