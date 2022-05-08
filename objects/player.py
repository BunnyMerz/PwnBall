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
        if x == self.x and y == self.y:
            return
        # TODO add collision check post movement and rollback (preferably using binary search) using tracing accordingly
        self.x = x
        self.y = y
        self.update_to_network()

    def encode(self): ## Encodes the Player obj to send trough the Network class
        data = ';'.join([str(x) for x in [self.x, self.y, self.id]])
        return 'PKT_U_Player/' + data ## Sending it as a str is more appropriate than bytes. Let the socket change it to bytes.

    def decode(string): ## Recives the encoded obj (encoded by player.encode(self)) as a string
        string = [float(x) for x in string.split(';')]
        return string # x,y,id

    def update_network(args): ## Recived message from Server. Args is a string
        # find by id
        args = Player.decode(args)
        x,y,id = args
        self = Player.find(id)
        self.x = x
        self.y = y
        print('Player',id,'moved to',x,y)

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
