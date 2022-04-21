from unittest import case
from animations import *
import pygame

class Player(Sprite):
    def __init__(self, x, y, animations, animation_tree, max_speeds, orientation=[1,0]):
        super().__init__(x, y, animations, animation_tree, max_speeds)
        self.orientation = orientation
    
    def move(self, inputs):
        speed = self.max_speeds[inputs['speed']]

        # inputs['left'] or inputs['up'] ## this is going opposite to self.orientation's vector
        # inputs['right'] or inputs['down'] ## this is towards it
        d = (inputs['right'] or inputs['down']) - (inputs['left'] or inputs['up'])
        self.x += self.orientation[0] * speed * d
        self.y += self.orientation[1] * speed * d

def create_player(x,y,orientation=[1,0]):
    if orientation[0] > orientation[1]:
        size = (10,10)
    else:
        size = (10,10)

    bar = pygame.Surface(size)
    bar.fill((100,80,20))
    box = Box(size[0],size[1])
    dbox = DetectionBox(box,0,0)

    f = Frame(bar,[dbox])
    a = Animation([f])
    player = Player(x,y,[a],{},{'normal':2,'fast':4},orientation)
    return player

