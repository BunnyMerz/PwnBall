from animations import *
import pygame

bar = pygame.Surface((100,10))
bar.fill((100,80,20))
box = Box(100,10)
dbox = DetectionBox(box,0,0)
f = Frame(bar,[dbox])
a = Animation([f])
sprite = Sprite(0,0,[a],{},{'normal':2,'fast':4})