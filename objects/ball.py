from typing import List
from animations import *
import pygame
import network

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

    def info(self) -> List:
        return [self.x,self.y,self.vx,self.vy]

class Ball(Sprite):
    balls = [] ## Entity already has entity[], but it is a nice shortcut for classes that use find() a lot
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y, animations, animation_tree)
        self.owner_id = 1 ## Network.connection_id
        self.bounces = [] ## Store bounces made client side, in case it gets desynced with the owner
        Ball.balls.append(self)

    def paint(self,color): ## Debugg temp function
        self.animations[0].frames[0].image.fill(color)

    ## Network related
    def encode(self):
        data = ';'.join([str(x) for x in [self.x, self.y, self.speed[0], self.speed[1], self.id, self.owner_id]])
        return 'PKT_U_Ball/'+data

    def decode(string):
        string = [float(x) for x in string.split(';')]
        return string # x,y,id

    def update_network(args): ## Recived message from Server. Args is a string encoded by ball.encode()
        # find by id
        args = Ball.decode(args)
        x,y,sx,sy,id,ow_id = args
        self = Ball.find(id)

        self.owner_id = ow_id ## Update the owner_id regardless of prediction.
        ## Check if it needs reconciliation
        if self.check_prediction(self,x,y,sx,sy):
            return # Dont update object if it is right (even if in the future)

        self.x = x
        self.y = y
        self.update_speed(Vector2(sx,sy),from_network=True)
        print('Updating ball pos to',x,y) ## debug

    def update_to_network(self):
        network.simulate_lag(
            network.Network.send,
            100,
            (self.encode())
        )
        # network.Network.send(self.encode())

    ######################

    def update_speed(self,new_speed, from_network=False):
        self.speed = new_speed
        print('ball:',self.owner_id, 'connection:', network.Network.connection_id)
        if not from_network and self.owner_id == network.Network.connection_id:
            self.decide_owner()
            self.update_to_network()

    def collided(self, collided_with_box, father_obj): ## Find the normal vector from collided_with and pass to bounce()

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
        self.store_bounce()
        self.update_speed(self.speed.reflect(normal_vector))

    def decide_owner(self): ## This will decide who should take care of this obj's updating
        if self.speed[1] < 0:
            self.owner_id = 1
        else:
            self.owner_id = 2

    def check_prediction(self,x,y,sx,sy) -> bool: ## Check if our prediction-side is faithful to the truth
        i = 1 # Not an actual index
        recent = Bounce(x,y,sx,sy)
        for bounce in self.bounces:
            if bounce == recent:
                self.bounces = self.bounces[i:] ## remove the bounce from the history, and any other behind it (in case there were packets lost)
                return True
            i += 1

        self.bounces = [] ## Predction is completly wrong, ignore the future
        return False

    def find(id):
        for b in Ball.balls:
            if b.id == id:
                return b

    def store_bounce(self):
        self.bounces.append(Bounce(self.x,self.y,self.speed[0],self.speed[1]))

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

    return ball

