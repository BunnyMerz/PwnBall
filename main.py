from time import sleep
from turtle import update
import pygame
from pygame.constants import *
from objects.player import *
from objects.ball import *
from objects.goal import Goal
from network import *
from controls import *
import sys

from objects.wall import Wall

class ScoreBoard():
    def __init__(self, amount_of_players) -> None:
        self.scores = [x for x in range(amount_of_players)]

    def score_callback(self):
        return lambda id,amount: self.update_score(id-1, amount)

    def update_score(self, player_index, amount):
        self.scores[player_index] += amount

pygame.init()

def main():
    player_count = len(Network.other_servers_ips)+1
    height = 600
    width = 600

    score_board = ScoreBoard(player_count)
    p1 = create_player(300,60)
    p2 = create_player(300,600-70)
    p3 = None
    p4 = None
    g1 = Goal(0,-100,600,100, score_board.score_callback(), 1)
    g2 = Goal(0,600,600,100, score_board.score_callback(), 2)
    g3 = None
    g4 = None
    if player_count >= 3:
        p3 = create_player(60,300,[0,1])
        g3 = Goal(-100,0,100,600, score_board.score_callback(), 3)
    else:
        Wall(50,0,20,600)

    if player_count == 4:
        p4 = create_player(600-70,300,[0,1])
        g4 = Goal(600,0,100,600, score_board.score_callback(), 4)
    else:
        Wall(width-70,0,20,600)

    goals = [g1,g2,g3,g4][:len(Network.other_servers_ips)+1]
    players = [p1, p2, p3, p4][:len(Network.other_servers_ips)+1]

    PlayerControls(players[Network.connection_id - 1], {'move_left': K_a,'move_right': K_d,'move_up': K_w,'move_down': K_s,'speed_up': K_LSHIFT})


    Wall(50,0,20,70)
    Wall(width-70,0,20,70)
    Wall(50,height-70,20,70)
    Wall(width-70,height-70,20,70)


    Wall(0,50,70,20)
    Wall(0,height-70,70,20)
    Wall(width-70,50,70,20)
    Wall(width-70,height-70,70,20)

    b1 = create_ball(100,340, Vector2(200,-500))
    b2 = create_ball(200,200, Vector2(-300,400))
    b3 = create_ball(230,220, Vector2(-200,340))
    b4 = create_ball(240,220, Vector2(-300,400))

    window = pygame.display.set_mode((width,height))#, pygame.NOFRAME)
    clock = pygame.time.Clock()
    
    update_time = 10 # ms
    t = 0

    while(1):
        delta_time = clock.tick(60) # ms
        t = t - int(t)
        t = delta_time/update_time

        for _ in range(int(t)):
            window.fill((30,30,30))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            PlayerControls.main(pygame.key.get_pressed())
            for e in Entity.entities:
                e.draw(window)

            for b in Ball.balls:
                b.update(update_time)
                for p in players + Wall.walls + goals:
                    b.has_collided(p)

                if b.x > width or b.x < 0 or b.y > height or b.y < 0:
                    print(Network.connection_id, b.owner_id)
                    

        pygame.display.update()

if __name__ == "__main__":
    main()