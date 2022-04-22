from re import X
from turtle import Vec2D
from unittest import case
from animations import *
import pygame
import network

class Player(Sprite):
    def __init__(self, x, y, animations, animation_tree, max_speeds, orientation=[1,0]):
        super().__init__(x, y, animations, animation_tree)
        self.orientation = orientation
        self.max_speeds = max_speeds
    
    def move(self, inputs):
        speed = self.max_speeds[inputs['speed']]

        # inputs['left'] or inputs['up'] ## this is going opposite to self.orientation's vector
        # inputs['right'] or inputs['down'] ## this is towards it
        d = (inputs['right'] or inputs['down']) - (inputs['left'] or inputs['up']) # 1, 0 or -1
        x = self.orientation[0] * speed * d
        y = self.orientation[1] * speed * d
        self.pos(self.x + x,self.y + y) # x += x but with collision detection.
    
    def pos(self,x,y):
        # TODO add collision check post movement and rollback (preferably using binary search) using tracing accordingly
        self.x = x
        self.y = y
        self.update_to_network()

    def encode(self):
        data = ';'.join([str(x) for x in [self.x, self.y, self.id]])
        return ('PKT_U_Player/' + data).encode()

    def decode(data):
        data = [float(x) for x in data.split(';')]
        return data # x,y,id

    def update_network(args): ## Recived message from Server. Args is a string
        # find by id
        args = Player.decode(args)
        x,y,id = args
        self = Player.find(id)
        self.x = x
        self.y = y

    def update_to_network(self):
        network.Network.send(self.encode())

def create_player(x,y,orientation=[1,0]): ## Just for debugging as of now. Possibly gonna become a spawn()
    if orientation[0] > orientation[1]:
        size = (100,10)
    else:
        size = (10,100)

    bar = pygame.Surface(size)
    bar.fill((100,80,20))
    box = Box(size[0],size[1])
    dbox = DetectionBox(box,0,0)

    f = Frame(bar,[dbox])
    a = Animation([f])
    player = Player(x,y,[a],{},{'normal':2,'fast':4},orientation)
    return player

class Ball(Sprite):
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y, animations, animation_tree)
        # self.owner = network.Network.connection_id

    def encode(self):
        data = ';'.join([str(x) for x in [self.x, self.y, self.speed[0], self.speed[1], self.id]])
        return ('PKT_U_Ball/'+data).encode()

    def decode(data):
        data = [float(x) for x in data.split(';')]
        return data # x,y,id

    def update_network(args): ## Recived message from Server. Args is a string
        # find by id
        args = Ball.decode(args)
        x,y,sx,sy,id = args
        self = Ball.find(id)
        self.x = x
        self.y = y
        self.update_speed(Vector2(sx,sy),from_network=True)

    def update_to_network(self):
        network.Network.send(self.encode())

    def update_speed(self,new_speed, from_network=False):
        self.speed = new_speed
        if not from_network:
            self.update_to_network()

    def collided(self, collided_with_box, father_obj): ## Find the normal vector from collided_with and pass to bounce()
        xy = father_obj.coords() + collided_with_box.coords() ## Real pos of DectionBox
        
        if isinstance(collided_with_box.shape, Circle):
            self.bounce(self.coords() - xy)

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
        self.update_speed(self.speed.reflect(normal_vector))

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


