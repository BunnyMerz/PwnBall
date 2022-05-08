from animations import *
from ball import Ball
import pygame
import network

class Goal(Sprite):
    def __init__(self, x, y, score_callback):
        super().__init__(x, y, [], {})
        self.score_callback = score_callback

    def collided(self, collided_with_box, father_obj):
        if isinstance(father_obj, Ball): ## Goal
            pass

    def draw(self,surface):
        return # making sure goal is never drawn