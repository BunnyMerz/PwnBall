from animations import *
import pygame
import network

class Ball(Sprite):
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y, animations, animation_tree)
        self.owner_id = 1 ## Network.connection_id

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
        self.x = x
        self.y = y
        self.owner_id = ow_id
        self.update_speed(Vector2(sx,sy),from_network=True)
        print('Updating ball pos to',x,y) ## debug

    def update_to_network(self):
        network.Network.send(self.encode())

    ######################

    def update_speed(self,new_speed, from_network=False):
        self.speed = new_speed
        print('ball:',self.owner_id, 'connection:', network.Network.connection_id)
        if not from_network and self.owner_id == network.Network.connection_id:
            self.decide_owner()
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

    def decide_owner(self): ## This will decide who should take care of this obj's updating
        if self.speed[1] < 0:
            self.owner_id = 1
        else:
            self.owner_id = 2

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

