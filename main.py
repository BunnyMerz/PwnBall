import pygame
from pygame.constants import *
from player import *
from controls import *
import sys

pygame.init()
height = 600
width = 600

p1 = create_player(0,0)
p2 = create_player(100,100,[0,1])
PlayerControls(p1,{'move_left': K_a,'move_right': K_d,'move_up': K_w,'move_down': K_s,'speed_up': K_LSHIFT})
PlayerControls(p2,{'move_left': K_LEFT,'move_right': K_RIGHT,'move_up': K_UP,'move_down': K_DOWN,'speed_up': K_RSHIFT})

window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
clock = pygame.time.Clock()

while(1):
    window.fill((0,0,0))
    delta_time = clock.tick(60)/1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    PlayerControls.main(pygame.key.get_pressed())
    p1.draw(window)
    p2.draw(window)

    pygame.display.update()