from animation.animations import *
from objects.ball import Ball
import pygame
import network
from random import randint as rng

class Goal(Sprite):
    goals = []
    def __init__(self, x, y, w, h, score_callback, player_id):
        # wall = pygame.Surface((w,h))
        dbox = DetectionBox(Box(w,h),0,0)
        a = Animation([Frame(None,[dbox])])
        super().__init__(x, y, [a], {})
        self.score_callback = score_callback
        self.player_id = player_id
        Goal.goals.append(self)

    def collided(self, collided_with_box, father_obj):
        if isinstance(father_obj, Ball): ## Goal
            p_id = network.Network.connection_id
            if father_obj.hide:
                return

            self.score_callback(self.player_id, 1)
            Ball.despawn(father_obj, self.score_callback,(self.player_id, -1))
            if father_obj.owner_id == p_id:
                msg = 'PKT_U_Goal'
                args = f'{self.player_id}'
                Ball.send_to_network(msg+'/'+args)

                direction = [
                    Vector2(rng(0,1000) - 500,600 - rng(0,200)),
                    Vector2(rng(0,1000) - 500,- 600 + rng(0,200)),
                    Vector2(600 - rng(0,200), rng(0,1000) - 500),
                    Vector2(-600 + rng(0,200), rng(0,1000) - 500),
                ][self.player_id-1]
                Ball.spawn([300,300,90,600-90][self.player_id-1],[90,600-90,300,300][self.player_id-1], direction)

    def update_network(args):
        id = args
        for g in Goal.goals:
            if g.player_id == id:
                g.score_callback(g.player_id, 1)
                return

    def draw(self,surface):
        return # making sure goal is never drawn