import pygame
from pygame.constants import *
from player import *
from network import *
from controls import *
import sys
import traceback

pygame.init()

def main(own_ip,own_port, their_ip, their_port, player_n):
    try:
        height = 600
        width = 600

        p1 = create_player(100,100)
        p2 = create_player(100,400)
        players = [p1,p2]
        PlayerControls(players[player_n], {'move_left': K_a,'move_right': K_d,'move_up': K_w,'move_down': K_s,'speed_up': K_LSHIFT})
        b1 = create_ball(100,340, Vector2(0,-5))
        b2 = create_ball(200,200, Vector2(-1,1))
        balls = [b1, b2]

        window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
        clock = pygame.time.Clock()
        
        Network.server = Server(own_ip,own_port)
        Network.server.start()
        Network.add_client(Client(their_ip,their_port))

        while(1):
            window.fill((30,30,30))
            delta_time = clock.tick(60)/1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            PlayerControls.main(pygame.key.get_pressed())
            for e in Entity.entities:
                e.draw(window)

            b1.update()
            b2.update()

            b1.has_collided(p1)
            b1.has_collided(p2)

            pygame.display.update()
    except:
        traceback.print_exc()
        input()