from pygame import Vector2
import itertools
# import pygame

class Entity():
    """Basic class. Used for basically anything that resides phisically in the game"""
    id_iter = itertools.count()
    next(id_iter)
    entities = []
    def __init__(self,x,y):
        ###
        self.id = next(Entity.id_iter) ## For debugging and sending over the network
        Entity.entities.append(self)
        ###
        self.x = x
        self.y = y

    def find(id):
        id = int(id)
        for e in Entity.entities:
            if e.id == id:
                return e

    def remove(entity):
        Entity.entities.remove(entity)

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
            frames,frame_duration=30,
            name='',
            loop_to_frame=0,starting_frame=0,
            transition_tree={},
            done = lambda : None, looped = lambda : None, transition = lambda : None
        ):

        self.name = name # for easier reading when setting up the sprite 
        self.frames = frames # [Frame(),...]

        self.starting_frame = starting_frame
        self.current_frame_i = starting_frame # int; frames[current_frame_i]
        self.loop_to_frame = loop_to_frame ## Which frame it should go to when reaching the end (useful for animations with a initial cast into a charge)
        self.transition_tree = transition_tree

        self.current_frame_count = 0 ## when current_frame_count > frame_duration, next_frame()
        self.frame_duration = frame_duration # ms

        ## configs
        self.reset_on_change = 1 ## If, when the animation loses focous, resets to the start of it
        self.loop = 1 ## If it should loop at all
        self.paused = 0 ## If the frame count should go up on update
        self.hide = 0 ## If it should be draw

        ## callbacks
        self.transition_priority = 1 ## checks agains other transitions to see if it should overwrite
        self.transition = transition ## will be called inside update() so it can transition to another animation at the right time
        self.done = done ## this will be called once the animation is done (but not when looping back)
        self.looped = looped ## this will be called once the animation is done and looping back to a spot

    # TODO call reset() somewhere when reset_on_change is true
    # TODO stop animation if it isn't set to loop (and call done())
    

    ### Called from outside
    def got_focous(self): ## Gets called when the class above focous on it
        if self.reset_on_change:
            self.reset()

    def interrupt(self): ## Whenever the animation ends by an external call
        pass

    def queue_transition(self,animation_name, force_change, sync):
        pass

    def play(self):
        self.paused = 0
    ###

    def reset(self): ## Resets to inital state
        self.current_frame_count = 0
        self.current_frame_i = self.starting_frame
        self.transition = lambda : None

    def current_frame(self):
        return self.frames[self.current_frame_i]
    
    def next_frame(self): ## Next frame (and loops if necessary). Will not reset timer
        self.current_frame_i += 1
        if self.current_frame_i >= len(self.frames):
            self.looped()
            if self.loop:
                self.current_frame_i = self.loop_to_frame
            else:
                self.paused = 1
                self.current_frame_i -= 1 ## keep in last frame

    def collisionboxes(self): ## Of the current frame
        return self.current_frame().collisionboxes
    def simple_collisionbox(self): ## Of the current frame
        return self.current_frame().simple_collisionbox()
    
    def draw(self,surface,x,y):
        if self.hide:
            return
        self.current_frame().draw(surface,x,y)

    def update(self,delta_time,multiplayer=1): ## Will try to advance the animation. Will not add to the timer if paused.
        if self.paused:
            return

        self.current_frame_count += delta_time*multiplayer

        ## transition_callback()
        while self.current_frame_count > self.frame_duration: # if frame is done
            self.current_frame_count -= self.frame_duration # skip to next section
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
        self.animation_tree = animation_tree # {'idle':0,'jump':1} with {'animation_name':state} for easier changing

        ## Movement. It would be more appropriate to be outside of sprite, but repeating on every sub-class would be tiring
        self.speed = Vector2()
        self.accel = Vector2()
        
        self.current_forces = [] # List of forces beeing applied on the current sprite; Example would be wind or gravity
        ##

    def draw(self,surface):
        self.current_animation().draw(surface,self.x,self.y)

    def current_animation(self):
        return self.animations[self.state]

    def queue_animation_change(self,animation_name_or_index, force_change=0, sync=0, transition_priority=1):
        """If 'animation_name_or_index' is a name, the name will be given to the current_animation()' and queued to be played based of the current_animation().transition_tree. If the name isn't found on the tree, it will immediatly be played.

        - Force_change will disregard the animation tree and will imediatly interrupt it, calling .interrupt() onto current_animation() and self.state will be changed. Force_change will not ignore transition_priority.

        - If sync is 1, it will wait until the current_animation()'s current frame ends so it can change to the given animation. This can synergize with force_change, as it will force the animation to change on the next possible frame, regardless of the transition_tree

        - Transition_priority is an int of any value and will decided if the animation that is being queued right now will override the transition currently waiting. It will override incase the value is the same or bigger than the one waiting.
        """
        if isinstance(animation_name_or_index,int):
            self.current_animation().interrupt()
            self.state = animation_name_or_index
        elif isinstance(animation_name_or_index,str):
            self.state = self.animation_tree[animation_name_or_index]
        self.current_animation().got_focous()

    def collisionboxes(self):
        return self.current_animation().collisionboxes()
    def simple_collisionbox(self):
        return self.current_animation().simple_collisionbox()

    def coords(self):
        return Vector2(self.x, self.y)

    def collided(self, collided_with_box, father_obj): ## Will be called once it collides with a certain hitbox
        pass

    def has_collided(self,other_sprite):
        own_boxes = self.collisionboxes()
        other_boxes = other_sprite.collisionboxes()

        ## If the generic boxes dont collide, none of the specific ones will
        if not Shape.has_collided(self.simple_collisionbox(), self.coords(),other_sprite.simple_collisionbox(), other_sprite.coords()):
            return False

        for own_box in own_boxes: ## n?? sadly lol
            for their_box in other_boxes:
                if Shape.has_collided(own_box, self.coords(), their_box, other_sprite.coords()):
                    self.collided(their_box, other_sprite)
                    other_sprite.collided(own_box, self)
                    return True

        return False

    def update(self,dt,multiplayer=1): ## Applies any time-based actions
        self.x += self.speed[0] * dt/1000
        self.y += self.speed[1] * dt/1000

        self.current_animation().update(dt,multiplayer)
        # TODO accel, animation, ...


####### Boxes

class Shape: ## Class for collision detection btw diff shapes. Tought about going an abstract path but was slightly hard, so opted for treating each case differently.
    def has_collided(db1,xy1: Vector2,db2,xy2: Vector2):
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
            # d = ((xy1[0] - xy2[0])**2 + (xy1[1] - xy2[1])**2)**(1/2)
            d = Vector2.distance_to(xy1,xy2)
            return d <= db1.shape.r + db2.shape.r

        return False

class DetectionBox:
    def __init__(self,shape,relative_x = 0, relative_y = 0):
        self.shape = shape
        ## Honestly, using relative coordinates has been a bit of a pain. I want to get the projection (normal vector of the surface of this detection box based on a point) of this box but bc of relative coordinates, I end up having to call the function higher up.
        self.rx = relative_x # relative x (relative to image it is attached to, in this project's case, Frame())
        self.ry = relative_y # relative y

    def coords(self):
        return Vector2(self.rx, self.ry)

    # def has_collided(self,other_detectionbox): ## Kinda useless as it needs to be attached to something (thus relativex)
    #     return Shape.has_collided(self.shape,(0,0),other_detectionbox.shape,(0,0))

    ## These could be virual attributes, but I learned about them too late
    def upper(self): ## All four functions are for creating a simplier box regardless of shape used.
        return self.shape.upper() + self.ry
    def lower(self):
        return self.shape.lower() + self.ry
    def left_most(self):
        return self.shape.left_most() + self.rx
    def right_most(self):
        return self.shape.right_most() + self.rx
    
    def define_simplebox(boxes): ## A box that generelizes others. Returns a DetectionBox made of shape.Box
        if len(boxes) == 0:
            return []

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

    def surface_vetor(self, point): ## Given a point, return a vector that represents the surface collided with
        pass

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

    def surface_vetor(self, point): ## Given a point, return a vector that represents the surface collided with
        pass

    def upper(self):
        return - self.r
    def lower(self):
        return self.r
    def left_most(self):
        return - self.r
    def right_most(self):
        return self.r