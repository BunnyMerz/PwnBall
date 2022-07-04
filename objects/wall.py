from animation.animations import *
import pygame
import network

class Wall(Sprite):
    walls = []
    def __init__(self, x, y, w, h, color=(100,200,200)):
        wall = pygame.Surface((w,h))
        wall.fill(color)
        dbox = DetectionBox(Box(w,h),0,0)
        a = Animation([Frame(wall,[dbox])])
        super().__init__(x, y, [a], {})

        Wall.walls.append(self)