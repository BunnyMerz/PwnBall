from typing import List

import numpy as np
from animation.animations import *
import pygame
import network

class Remove(): ## Using a class instead of a const incase I want to change how it behaves later. Keeping the pattern
    def __init__(self, id, rollback_fn=lambda *args: None, args=()):
        self.id = id
        self._rollback = rollback_fn
        self._args = args

    def __eq__(self, __o) -> bool:
        if isinstance(__o, Remove):
            return True
        return False

    def rollback(self):
        self._rollback(*self._args)
        Ball.find(self.id).hide = 0

    def __repr__(self) -> str:
        return str([self.id, self._rollback, self._args])

class Bounce(): ## Any change in pos and or speed
    def __init__(self,x,y,vx,vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def __eq__(self, __o) -> bool:
        if isinstance(__o, Bounce):
            return self.info() == __o.info()
        
        return False

    def __repr__(self) -> str:
        return str(self.info())

    def info(self) -> List:
        return [self.x,self.y,self.vx,self.vy]

    def rollback(self):
        return ## nothing to rollback

class Ball(Sprite):
    balls = [] ## Entity already has entity[], but it is a nice shortcut for classes that use find() a lot
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y, animations, animation_tree)
        self.owner_id = 1 ## Network.connection_id
        self.history = [] ## Store bounces and scores made client side, in case it gets desynced with the owner
        self.hide = 0 ## For client-side pseudo-removal
        Ball.balls.append(self)

    def draw(self, surface):
        if self.hide:
            return

        # a = self.current_animation().current_frame().image
        # if network.Network.connection_id == self.owner_id:
        #     a.fill((10,200,30))
        # else:
        #     a.fill((10,20,230))

        super().draw(surface)

    def paint(self,color): ## Debugg temp function
        self.animations[0].frames[0].image.fill(color)

    ## Network related
    def encode(self):
        data = ';'.join([str(x) for x in [self.x, self.y, self.speed[0], self.speed[1], self.id, self.owner_id]])
        return data

    def decode(string):
        string = [float(x) for x in string.split(';')]
        return string # x,y,id

    def spawn(x,y,speed):
        create_ball(x,y,speed)
        msg = 'PKT_S_Ball'
        args = f'{x};{y};{speed[0]};{speed[1]}'
        Ball.send_to_network(msg+'/'+args)

    def despawn(self, _rollback=lambda *args: None, _args=()): ## Whenever the ball goes offscreen
        ## Dont remove it, if you aren't the owner
        if self.owner_id == network.Network.connection_id:
            Ball.remove(self)
            msg = 'PKT_R_Ball'
            args = f'{self.id}'
            Ball.send_to_network(msg+'/'+args)
        else:
            self.hide = 1
            self.history.append(Remove(self.id,_rollback,_args))

    def remove(ball):
        Ball.balls.remove(ball)
        Entity.remove(ball)

    def remove_network(args): ## PKT_R_Ball/id
        id = NetworkBall.PKT_R_Ball(args)
        b = Ball.find(id)
        if b == None:
            return

        if b.check_prediction(Remove(b.id)):
            Ball.remove(b) ## if he is right, actually remove the obj form list
        ## check_prediction() will take care if it is false

    def update_network(args): ## PKT_U_Ball/self.encode()
        # find by id
        args = Ball.decode(args)
        x,y,vx,vy,id,ow_id = args

        self = Ball.find(id)
        if self == None:
            return

        self.owner_id = int(ow_id) ## Update the owner_id regardless of prediction.
        ## Check if it needs reconciliation
        
        if self.check_prediction(Bounce(x,y,vx,vy)):
            return # Dont update object if it is right (even if in the future)
        ## check_prediction() will rollback actions if needed


        self.x = x
        self.y = y
        self.update_speed(Vector2(vx,vy),from_network=True)
        # print('Updating ball pos to',x,y) ## debug

    def spawn_network(args):
        x,y,vx,vy = args.split(';')
        create_ball(float(x),float(y),Vector2(float(vx),float(vy)))

    def send_to_network(message):
        network.Network.send(message)

    ######################

    def update_speed(self,new_speed, from_network=False):
        if self.hide:
            return
        self.speed = new_speed
        # print('ball:',self.owner_id, 'connection:', network.Network.connection_id)
        if not from_network and self.owner_id == network.Network.connection_id:
            self.decide_owner()
            msg = f'PKT_U_Ball/{self.encode()}'
            Ball.send_to_network(msg)

    def collided(self, collided_with_box, father_obj): ## Find the normal vector from collided_with and pass to bounce()   
        if self.hide:
            return 
        from objects.goal import Goal
        if isinstance(father_obj, Goal):
            return
        #This is the annoyance of hbox using relative coords, it requires the father obj in the function to find its(hbox's) anchor
        xy = father_obj.coords() + collided_with_box.coords() ## Real pos of DectionBox
        
        if isinstance(collided_with_box.shape, Circle):
            self.bounce(self.coords() - xy) ## normal vector

        if isinstance(collided_with_box.shape, Box):
            p1 = xy
            p2 = xy + Vector2(collided_with_box.right_most(),0)
            p3 = xy + Vector2(0,collided_with_box.lower())
            p4 = xy + Vector2(collided_with_box.right_most(),collided_with_box.lower())

            d = []
            for p in [p1,p2,p3,p4]:
                d.append(Vector2.distance_squared_to(self.coords(),p))

            d1,d2,d3,d4 = d
            ds = [(d1,p1),(d2,p2),(d3,p3),(d4,p4)]
            ds.sort(key= lambda x: x[0])

            if ds[1][0] != ds[2][0]:
                v = ds[0][1] - ds[1][1]
                v = Vector2(-v[0],v[1])
                self.bounce(v)

    def bounce(self,normal_vector):
        if self.hide:
            return
        self.update_speed(self.speed.reflect(normal_vector))
        self.store_bounce()

    def decide_owner(self): ## This will decide who should take care of this obj's updating
        a = Vector2(-self.x+70,-self.y+70)
        b = Vector2(600-self.x-70,-self.y+70)
        c = Vector2(600 - self.x - 70,600 - self.y - 70)
        d = Vector2(-self.x + 70,600 - self.y - 70)
        r = {3:1,12:2,9:3,6:4}
        smallest = []
        names = [1,2,4,8]
        self.owner_id = None
        for x in range(4):
            p = [a,b,c,d][x]
            smallest.append(abs(p.angle_to(self.speed)))

        print(smallest)
        x = sum([x for _, x in sorted(zip(smallest, names))[:2]])

        self.owner_id = r[x]

        if self.owner_id == None:
            # print("Ball decided as None",self.id)
            self.owner_id = 1
        if self.owner_id > len(network.Network.other_servers_ips)+1:
            # print("Ball out of player range",self.id,self.owner_id)
            self.owner_id = 1



    def check_prediction(self,recieved_action) -> bool: ## Check if our prediction-side is faithful to the truth
        i = 1 # Not an actual index
        for act in self.history:
            if act == recieved_action:
                self.history = self.history[i:] ## remove the bounce from the history, and any other behind it (in case there were packets lost)
                return True
            i += 1

        self.rollback(self.history)
        self.history = [] ## Predction is completly wrong, ignore the future
        return False

    def rollback(self,actions):
        # a = ["$$ Prediction wrong! rollbacking the following:"]
        for act in actions:
            # a.append("$ - " + str(act))
            act.rollback()
        # print('\n'.join(a))

    def find(id): ## Overwrites entities' find, for efficiency
        for b in Ball.balls:
            if b.id == id:
                return b

    def store_bounce(self):
        self.history.append(Bounce(self.x,self.y,self.speed[0],self.speed[1]))

def create_ball(x,y,speed=Vector2(0,1)):
    r =  7

    image = pygame.Surface((r*2,r*2))
    image.set_colorkey((0,0,0))
    pygame.draw.circle(image,(40,60,80),(r,r),r)
    box = Circle(r)
    dbox = DetectionBox(box,r,r)
    f = Frame(image,[dbox])
    a = Animation([f])
    ball = Ball(x,y,[a],{})
    ball.speed = speed

    ball.decide_owner()
    return ball

class NetworkBall():

    def PKT_U_Ball(args):
        return

    def PKT_R_Ball(args):
        return int(args)
    
    def PKT_S_Ball(args):
        return

