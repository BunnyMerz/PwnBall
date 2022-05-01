from time import sleep
import pygame
from pygame.constants import *
from objects.player import *
from objects.ball import *
from network import *
from controls import *
import sys
import traceback

pygame.init()

def main():
    worked = False
    while(not(worked)):
        try:
            own_ip = input("Your won ip, please. [0.0.0.0]: ")
            own_port = input("Choose a port (2-4 digits, no 6969 pls): ")
            own_port = int(own_port)
            Network.start(own_ip,own_port)
            worked = True
        except:
            print("An exception occured:")
            print("##############")
            traceback.print_exc()
            print("##############")

    height = 600
    width = 600

    p1 = create_player(100,100)
    p2 = create_player(100,400)
    players = [p1,p2]
    your_controls = PlayerControls(players[Network.connection_id - 1], {'move_left': K_a,'move_right': K_d,'move_up': K_w,'move_down': K_s,'speed_up': K_LSHIFT})
    b1 = create_ball(100,340, Vector2(0,-5))
    b2 = create_ball(200,200, Vector2(-1,1))
    balls = [b1, b2]

    window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
    clock = pygame.time.Clock()
    

    while(Network.clients == []):
        addr = input("Input their ip [0.0.0.0:6969] or press enter if they already connected: ")
        try:
            ip, port = addr.split(':')
            port = int(port)
        except:
            print("Malformed address or skipped direct connection.")
        try:
            Network.connect_to(ip,port)
            your_controls.player = players[Network.connection_id - 1]
        except:
            print('Something happend when trying to connect')
            print("##############")
            traceback.print_exc()
            print("##############")

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

if __name__ == "__main__":
    main()