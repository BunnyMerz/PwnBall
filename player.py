from unittest import case
from animations import *
import pygame

class Player(Sprite):
    def __init__(self, x, y, animations, animation_tree, max_speeds, orientation=[1,0]):
        super().__init__(x, y, animations, animation_tree)
        self.orientation = orientation
        self.max_speeds = max_speeds
    
    def move(self, inputs):
        speed = self.max_speeds[inputs['speed']]

        # inputs['left'] or inputs['up'] ## this is going opposite to self.orientation's vector
        # inputs['right'] or inputs['down'] ## this is towards it
        d = (inputs['right'] or inputs['down']) - (inputs['left'] or inputs['up'])
        x = self.orientation[0] * speed * d
        y = self.orientation[1] * speed * d
        self.pos(self.x + x,self.y + y)
    
    def pos(self,x,y):
        # TODO add collision check post movement and rollback using tracing accordingly
        self.x = x
        self.y = y

def create_player(x,y,orientation=[1,0]):
    if orientation[0] > orientation[1]:
        size = (100,10)
    else:
        size = (10,100)

    bar = pygame.Surface(size)
    bar.fill((100,80,20))
    box = Box(size[0],size[1])
    dbox = DetectionBox(box,0,0)

    f = Frame(bar,[dbox])
    a = Animation([f])
    player = Player(x,y,[a],{},{'normal':2,'fast':4},orientation)
    return player

class Ball(Sprite):
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y, animations, animation_tree)

def create_ball(x,y,speed=[0,1]):
    r =  7

    image = pygame.Surface((r*2,r*2))
    image.set_colorkey((0,0,0))
    pygame.draw.circle(image,(10,20,40),(r,r),r)
    box = Circle(r)
    dbox = DetectionBox(box,r,r)
    f = Frame(image,[dbox])
    a = Animation([f])
    ball = Ball(x,y,[a],{})
    ball.speed = speed

    return ball
