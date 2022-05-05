from time import sleep
import pygame
from pygame.constants import *
from objects.player import *
from objects.ball import *
from network import *
from controls import *
import sys
import traceback

from objects.wall import Wall

pygame.init()

def main():
    own_ip = 'localhost'
    own_port = 222
    Network.start(own_ip,own_port)

    height = 600
    width = 600

    p1 = create_player(100,200)
    p2 = create_player(100,590)
    players = [p1,p2]
    your_controls = PlayerControls(players[Network.connection_id - 1], {'move_left': K_a,'move_right': K_d,'move_up': K_w,'move_down': K_s,'speed_up': K_LSHIFT})
    b1 = create_ball(100,340, Vector2(2,-5))

    Wall(0,0,10,600)
    Wall(590,0,10,600)
    Wall(0,-1,600,1)
    Wall(0,601,600,1)

    window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
    clock = pygame.time.Clock()
    

    Network.connect_to('localhost',111)
    your_controls.player = players[Network.connection_id - 1]

    while(1):

        window.fill((30,30,30))
        delta_time = clock.tick(60)/1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        PlayerControls.main(pygame.key.get_pressed())
        for e in Entity.entities:
            e.draw(window)

        if b1.owner_id == network.Network.connection_id:
            b1.paint((10,200,30))
        else:
            b1.paint((100,20,240))

        b1.update()

        for e in Entity.entities:
            if b1 != e:
                b1.has_collided(e)

        pygame.display.update()

if __name__ == "__main__":
    main()