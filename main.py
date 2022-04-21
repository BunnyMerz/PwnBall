import pygame
from player import *
import sys

pygame.init()
height = 600
width = 600

window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
clock = pygame.time.Clock()

while(1):
    delta_time = clock.tick(60)/1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    sprite.draw(window)

    pygame.display.update()