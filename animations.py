from matplotlib import animation
from pygame import Vector2

class Entity():
    id = 1
    def __init__(self,x,y):
        ###
        self.entity_id = Entity.id
        Entity.id += 1
        ###
        self.x = x
        self.y = y

class Frame():
    """Represents a single frame with specialboxes, or a still image"""
    def __init__(self,image, collisionboxes=[]):
        self.image = image # pygame.Surface
        self.collisionboxes = collisionboxes
        self.simplebox = DetectionBox.define_simplebox(self.collisionboxes)
    
    def draw(self,surface,x,y):
        surface.blit(self.image,(x,y))

    def simple_collisionbox(self):
        return self.simplebox

    def width(self):
        return self.image.get_width()
    def height(self):
        return self.image.get_height()


class Animation():
    """Has a collection of frames, with how long they should play, which frame the animation is, etc..."""
    def __init__(
            self,
            frames,frame_duration=[],
            name='',
            loop_to_frame=0,starting_frame=0,
            done = lambda x : None
        ):

        self.name = name # for easier reading when setting up the sprite 
        self.frames = frames # [Frame()]

        self.starting_frame = starting_frame
        self.current_frame_i = starting_frame # int; frames[current_frame_i]
        self.loop_to_frame = loop_to_frame

        self.current_frame_count = 0 ## Delay of current frame; current_frame_count < frame_duration[current_frame]
        self.frame_duration = frame_duration

        ## configs
        self.reset_on_change = 1 ## If the animation loses focous, should it reset to the start of it?
        self.loop = 1
        self.paused = 0
        self.hide = 0

        ## callbacks
        self.done = done ## this will be called once the animation is done (or about to loop)

    # TODO call reset() somewhere when reset_on_change is true

    def reset(self):
        self.current_frame_count = 0
        self.current_frame_i = self.starting_frame

    def current_frame(self):
        return self.frames[self.current_frame_count]
    
    def next_frame(self):
        self.current_frame_i += 1
        if self.current_frame_i >= len(self.frames):
            self.done()
            self.current_frame_i = self.loop_to_frame

    def collisionboxes(self):
        return self.current_frame().collisionboxes
    def simple_collisionbox(self):
        return self.current_frame().simple_collisionbox()
    
    def draw(self,surface,x,y):
        if self.hide:
            return
        self.current_frame().draw(surface,x,y)

    def update(self,delta_frame):
        if self.paused:
            return

        self.current_frame_count += delta_frame

        while self.current_frame_count > self.frame_duration[self.current_frame_i]: # if frame is done
            self.current_frame_count -= self.frame_duration[self.current_frame_i] # skip to next section
            self.next_frame() #

    def config(self,loop,paused,hide,reset_on_change):
        self.loop = loop
        self.paused = paused
        self.hide = hide
        self.reset_on_change = reset_on_change

class Sprite(Entity):
    def __init__(self, x, y, animations, animation_tree, max_speeds={'default':2}):
        super().__init__(x, y)
        ## Animation
        self.animations = animations
        self.state = 0 ## Each state should represent an animation
        self.animation_tree = animation_tree # {'idle':0,'jump':1} with 'animation_name':state

        ## Movement
        self.speed = Vector2() # pygame
        self.accel = Vector2()
        
        self.max_speeds = max_speeds # x/frame
        self.current_forces = [] # List of forces beeing applied on the current sprite; Example would be wind or gravity
        ##

    def draw(self,surface):
        self.current_animation().draw(surface,self.x,self.y)

    def current_animation(self):
        return self.animations[self.state]

    def change_animation(self,animation_name):
        self.state = self.animation_tree[animation_name]

    def collisionboxes(self):
        return self.current_animation().collisionboxes()
    def simple_collisionbox(self):
        return self.current_animation().simple_collisionbox()

    def collided(self,other_sprite):
        own_boxes = self.collisionboxes()
        other_boxes = other_sprite.collisionboxes()

        ## If the generic boxes dont collide, none of the specific ones will
        if not Shape.collided(self.simple_collisionbox(), self.coords(),other_sprite.simple_collisionbox(), self.coords()):
            return False

        for own_bow in own_boxes: ## n² sadly lol
            for their_box in other_boxes:
                if Shape.collided(own_bow, self.coords(), their_box, other_sprite.coords()):
                    return True

        return False


####### Boxes

class Shape:
    def collided(db1,xy1,db2,xy2):
        ## have diff detection for diff shapes pairs

        ## box x circle

        ## box x box
        if isinstance(db1.shape, Box) and isinstance(db2.shape, Box):
            x1,y1 = db1.rx + xy1[0], db1.ry + xy1[1]
            x2,y2 = db1.shape.width + x1, db1.shape.height + y1

            a1,b1 = db2.rx + xy1[0], db2.ry + xy1[1]
            a2,b2 = db2.shape.width + x1, db2.shape.height + y1

            if (x1 < a2 and
                x2 > a1 and
                y1 < b2 and
                y2 > b1):
                return True

        ## circle x circle

        return False

class DetectionBox:
    def __init__(self,shape,relative_x = 0, relative_y = 0):
        self.shape = shape
        self.rx = relative_x # relative x
        self.ry = relative_y # relative y

    def collided(self,other_detectionbox):
        return Shape.collided(self.shape,other_detectionbox.shape)

    def upper(self):
        return self.shape.upper() + self.ry
    def lower(self):
        return self.shape.lower() + self.ry
    def left_most(self):
        return self.shape.left_most() + self.rx
    def right_most(self):
        return self.shape.right_most() + self.rx
    
    def define_simplebox(boxes): ## A box that generelizes others. Returns a DetectionBox made of shape.Box
        x,y = boxes[-1].left_most(),boxes[-1].upper() ## need lowest possible number
        x2,y2 = boxes[-1].right_most(),boxes[-1].lower() ## need highest possible number
        for box in boxes[:-1]: # we already checked the last one on the last 2 lines
            x = min(x,box.left_most())
            y = min(y,box.upper())
            x2 = min(x2,box.right_most())
            y2 = min(y2,box.lowwer())
        b = Box(x2-x,y2-y)
        simpleb = DetectionBox(b,x,y)
        
        return simpleb

class CollisionBox(DetectionBox):
    def __init__(self, shape, relative_x=0, relative_y=0):
        super().__init__(shape, relative_x, relative_y)


class Box:
    def __init__(self,width,height):
        self.width = width
        self.height = height

    def upper(self):
        return 0
    def lower(self):
        return self.height
    def left_most(self):
        return 0
    def right_most(self):
        return self.width

class Circle:
    def __init__(self,r):
        self.r = r

    def upper(self):
        return - self.r
    def lower(self):
        return self.r
    def left_most(self):
        return - self.r
    def right_most(self):
        return self.r