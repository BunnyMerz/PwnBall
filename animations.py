from matplotlib import animation
from pygame import Vector2

class Entity():
    """Basic class. Used for basically anything that resides phisically in the game"""
    id = 1
    entities = []
    def __init__(self,x,y):
        ###
        self.entity_id = Entity.id ## For debugging and sending over the network
        Entity.id += 1
        Entity.entities.append(self)
        ###
        self.x = x
        self.y = y

class Frame():
    """Represents a single frame with specialboxes, or a still image"""
    def __init__(self,image, collisionboxes=[]):
        self.image = image # pygame.Surface
        self.collisionboxes = collisionboxes ## Multiple ones for complex formats
        self.simplebox = DetectionBox.define_simplebox(self.collisionboxes) ## Covers all collision boxes for a faster detection (simple case to avoid uneeded tests)
    
    def draw(self,surface,x,y):
        surface.blit(self.image,(x,y)) ## Requires x and y since they aren't entities.

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
            done = lambda x : None, looped = lambda x : None
        ):

        self.name = name # for easier reading when setting up the sprite 
        self.frames = frames # [Frame(),...]

        self.starting_frame = starting_frame
        self.current_frame_i = starting_frame # int; frames[current_frame_i]
        self.loop_to_frame = loop_to_frame ## Which frame it should go to when reaching the end (useful for animations with a initial cast into a charge)

        self.current_frame_count = 0 ## Delay of current frame; current_frame_count < frame_duration[current_frame]
        self.frame_duration = frame_duration ## How long each frame should last

        ## configs
        self.reset_on_change = 1 ## If, when the animation loses focous, resets to the start of it
        self.loop = 1 ## If it should loop at all
        self.paused = 0 ## If the frame count should go up on update
        self.hide = 0 ## If it should be draw

        ## callbacks
        self.done = done ## this will be called once the animation is done (but not when looping back)
        self.looped = looped ## this will be called once the animation is done and looping back to a spot

    # TODO call reset() somewhere when reset_on_change is true
    # TODO stop animation if it isn't set to loop (and call done())

    def reset(self): ## Resets to inital state
        self.current_frame_count = 0
        self.current_frame_i = self.starting_frame

    def current_frame(self):
        return self.frames[self.current_frame_i]
    
    def next_frame(self): ## Next frame (and loops if necessary). Will not reset timer
        self.current_frame_i += 1
        if self.current_frame_i >= len(self.frames):
            self.looped()
            self.current_frame_i = self.loop_to_frame

    def collisionboxes(self): ## Of the current frame
        return self.current_frame().collisionboxes
    def simple_collisionbox(self): ## Of the current frame
        return self.current_frame().simple_collisionbox()
    
    def draw(self,surface,x,y):
        if self.hide:
            return
        self.current_frame().draw(surface,x,y)

    def update(self,delta_frame): ## Will try to advance the animation. Will not add to the timer if paused.
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
    def __init__(self, x, y, animations, animation_tree):
        super().__init__(x, y)
        ## Animation
        self.animations = animations
        self.state = 0 ## Each state should represent an animation
        self.animation_tree = animation_tree # {'idle':0,'jump':1} with 'animation_name':state for easier changing

        ## Movement. It would be more appropriate to be outside of sprite, but repeating on every sub-class would be tiring
        self.speed = Vector2()
        self.accel = Vector2()
        
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

    def coords(self):
        return Vector2(self.x, self.y)

    def collided(self,other_sprite):
        own_boxes = self.collisionboxes()
        other_boxes = other_sprite.collisionboxes()

        ## If the generic boxes dont collide, none of the specific ones will
        if not Shape.collided(self.simple_collisionbox(), self.coords(),other_sprite.simple_collisionbox(), other_sprite.coords()):
            return False

        for own_bow in own_boxes: ## n² sadly lol
            for their_box in other_boxes:
                if Shape.collided(own_bow, self.coords(), their_box, other_sprite.coords()):
                    return True

        return False

    def update(self,dt=0): ## Applies any time-based actions
        self.x += self.speed[0]
        self.y += self.speed[1]
        # TODO accel, animation, ...


####### Boxes

class Shape: ## Class for collision detection btw diff shapes. Tought about going an abstract path but was slightly hard, so opted for treating each case differently.
    def collided(db1,xy1,db2,xy2):
        ## box x circle
        if (isinstance(db1.shape, Box) and isinstance(db2.shape, Circle)) or (isinstance(db2.shape, Box) and isinstance(db1.shape, Circle)): ## No idea for a better if
            return True

        ## box x box
        if isinstance(db1.shape, Box) and isinstance(db2.shape, Box):
            ## Getting upper-left and bottom-right points.
            x1,y1 = db1.rx + xy1[0], db1.ry + xy1[1]
            x2,y2 = db1.shape.width + x1, db1.shape.height + y1

            a1,b1 = db2.rx + xy2[0], db2.ry + xy2[1]
            a2,b2 = db2.shape.width + a1, db2.shape.height + b1
            ####

            return not((x1 > a2 or x2 < a1) or (y1 > b2 or y2 < b1)) ## Tests for a no-collision, so returns not(no-collision)

        ## circle x circle
        if isinstance(db1.shape, Circle) and isinstance(db2.shape, Circle):
            xy1 += Vector2(db1.shape.r,db1.shape.r) ## Getting the center of the circle
            xy2 += Vector2(db2.shape.r,db2.shape.r) ## Scuffed lol
            d = ((xy1[0] - xy2[0])**2 + (xy1[1] - xy2[1])**2)**(1/2)
            return d <= db1.shape.r + db2.shape.r

        return False

class DetectionBox:
    def __init__(self,shape,relative_x = 0, relative_y = 0):
        self.shape = shape
        self.rx = relative_x # relative x (relative to image it is attached to, in this case, Frame())
        self.ry = relative_y # relative y

    def collided(self,other_detectionbox): ## Kinda useless as it needs to be attached to something (thus rx)
        return Shape.collided(self.shape,(0,0),other_detectionbox.shape,(0,0))

    def upper(self): ## All four functions are for creating a simplier box regardless of shape used.
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
            x2 = max(x2,box.right_most())
            y2 = max(y2,box.lowwer())
        b = Box(x2-x,y2-y)
        simpleb = DetectionBox(b,x,y)
        
        return simpleb

class Box:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        ## No x nor y since they are just meant for shape-making

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
        ## Width doesnt make sense on a circle, so the idea of upper/lower/left/right came into mind.

    def upper(self):
        return - self.r
    def lower(self):
        return self.r
    def left_most(self):
        return - self.r
    def right_most(self):
        return self.r