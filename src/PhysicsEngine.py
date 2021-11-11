import pymunk
import pygame

pygame.init()

display = pygame.display.set_mode((640,480))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = 0,-1000
FPS = 60

def convert_coordinates(point):
    return point[0],480-point[1]

class Player():
    def __init__(self,size,collision_type):
        self.body = pymunk.Body()
        self.body.position = 0,0
        self.body.velocity = 10,0
        self.size = size
        self.shape = pymunk.Poly(self.body,[(0, 0), (size, 0), (0, size), (0, size)])
        self.shape.density = 1
        self.shape.collision_type = collision_type

    def draw(self,display):
        pygame.draw.rect(display, (0, 255, 0), convert_coordinates(self.body.position), 3)

def collide(arbiter, space, data):
    print("HELLo")
    return True

body = pymunk.Body()
body.position = 120,300
shape = pymunk.Circle(body,10)
shape.density = 1
shape.collision_type = 1
space.add(body,shape)

platform_body = pymunk.Body(body_type=pymunk.Body.STATIC)
platform_shape = pymunk.Segment(platform_body,(0,50),(640,50),3)
space.add(platform_body,platform_shape)

box = pymunk.Body(body_type=pymunk.Body.STATIC)
#box.position = 120,100
w = 50
h = w
vs = [(-w/2,-h/2), (w/2,-h/2), (w/2,h/2), (-w/2,h/2)]
#vs = [(0,0),(0,50),(50,50),(0,50)]
t = pymunk.Transform(tx=w/2+100, ty=h/2+100)
boxshape = pymunk.Poly(box, vs, transform=t)
boxshape.collision_type = 2
boxshape.density = 1
space.add(box,boxshape)

def game():
    handler = space.add_collision_handler(1,2)
    handler.pre_solve = collide

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        display.fill((0,0,0))
        x,y = convert_coordinates(body.position)
        pygame.draw.circle(display,(255,0,0),(int(x),int(y)),10)
        pygame.draw.line(display,(255,255,255),convert_coordinates((0,50)),convert_coordinates((640,50)),3)
        print(boxshape.get_vertices())
        #print([convert_coordinates(p) for p in boxshape.get_vertices()])
        pygame.draw.polygon(display,(0,255,0),[convert_coordinates(p) for p in boxshape.get_vertices()],3)

        pygame.display.update()
        clock.tick(FPS)
        space.step(1/FPS)

game()
pygame.quit()