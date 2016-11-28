
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from common.clock import *

SPACESHIP_X = 100
NOW_X = 300
RET_X = 350 # TODO: see if need to update with song?
WINDOW_SIZE = (1280, 720)

# TODO: better scroll speed / fix jittery-looking scrolling
# It has to do with how scrolling is synced to the song frame. It's 100% synced but it gets jittery at high scroll speeds
PIXELS_PER_TICK = 0.25

class Spaceship(InstructionGroup):
    """
    The spaceship that the user controls.
    """

    def __init__(self, x, y):
        super(Spaceship, self).__init__()
        self.x = x
        self.y = y
        self.max_y = 559
        self.min_y = 161

        # TODO make it the image
        self.rect = Rectangle(pos=(self.x-80, self.y-40), size=(140,80))
        self.add(self.rect)

    def move_vertical(self, pos=None, step=0):
        """
        Update vertical position of the spaceship so it can move up and down
        """
        if pos:
            self.y = pos
        if step:
            self.y += step

        if self.y > self.max_y:
            self.y = self.max_y
        elif self.y < self.min_y:
            self.y = self.min_y

        self.rect.pos = (self.x-80, self.y-40)

    def on_update(self, dt):
        pass


class NowPillar(InstructionGroup):
    """
    The pillar that the user needs to hit objects with the laser.
    """

    def __init__(self):
        super(NowPillar, self).__init__()
        self.add(Color(rgb=[0.9, 0.9, 0.9]))
        self.add(Line(width=4, points=[NOW_X - 20, 360 - 80 - 160, NOW_X - 20, 360 + 80 + 160]))

    def on_update(self, dt):
        pass
        
class BeatLine(InstructionGroup):
    """
    Lines that go along with the beat to help the user follow the beat.
    """
    def __init__(self, count, tick):
        super(BeatLine, self).__init__()

        self.add(Color(rgb=[0.5, 0.5, 0.5], a=0.8))
        x = NOW_X + tick * PIXELS_PER_TICK
        width = 3 if count == 1 else 1
        self.add(Line(width=width, points=[x, 360 - 80 - 160, x, 360 + 80 + 160]))

class Laser(InstructionGroup):
    """
    The projectile laser that is "shot" when the user fires.
    TODO, might just be part of the BEAM class
    """

    def __init__(self):
        super(Laser, self).__init__()

    def on_update(self, dt):
        pass


class Rocket(InstructionGroup):
    """
    Rocket object that is shot when the user fires.
    """

    def __init__(self):
        super(Rocket, self).__init__()

    def on_update(self, dt):
        pass


class Beam(InstructionGroup):
    """
    This is the object that shows where the ship is aiming.
    """

    def __init__(self, ship_x, ship_y, aim='mid'):
        super(Beam, self).__init__()

        self.ship_x = ship_x
        self.ship_y = ship_y

        self.set_aim(aim)

        # add red first so that blue is on top
        # self.add(Color(rgb=[1, 0.5, 0.5], a=0.3))
        # self.red_line = Line(points=[ship_x, ship_y, RET_X, self.reticle_y], width=3)
        # self.add(self.red_line)

        self.add(Color(rgb=[0.5, 0.5, 1], a=0.3))
        #self.blue_line = Line(points=[ship_x, ship_y, NOW_X - 20, self.now_aim_y], width=3)
        #self.add(self.blue_line)

    def set_aim(self, aim):
        """
        This DOES NOT update update the points
        """
        if aim == 'mid':
            self.now_aim_y = 360
            self.reticle_y = 360
        elif aim == 'top':
            self.now_aim_y = 360 + 180
            self.reticle_y = 360 + 180
        else:
            self.now_aim_y = 360 - 180
            self.reticle_y = 360 - 180

    def update_points(self, ship_y):
        self.ship_y = ship_y
        #self.blue_line.points = [self.ship_x, self.ship_y, NOW_X - 20, self.now_aim_y]
        #self.red_line.points = [self.ship_x, ship_y, RET_X, self.reticle_y]

    def on_update(self, dt):
        pass


class Target(InstructionGroup):
    """
    Abstract class for characteristics common among all types of
    targets that the user will fire at.
    """

    def __init__(self, lane, tick, length):
        super(Target, self).__init__()
        self.lane = lane
        self.tick = tick
        self.x = NOW_X + tick * PIXELS_PER_TICK
        self.y = self.vertical_pos_from_lane(lane)
        self.length = length
        self.hit = False
        self.destroyed_with = "laser"

    def destroy(self):
        pass

    def in_tick_range(self, start_tick, end_tick):
        # TODO see if should be just implemented by children
        if self.destroyed_with == 'laser':
            return start_tick < self.tick < end_tick
        else:
            # Bomb target TODO make in actual range
            return start_tick < self.tick - self.length < end_tick

    def vertical_pos_from_lane(self, lane):
        if lane == 'top':
            return 360 + 160
        elif lane == 'mid':
            return 360
        else:
            return 360 - 160

    def on_update(self, dt):
        pass


class Tap(Target):
    """
    Targets that the user will destroy with a single laser.
    """

    def __init__(self, lane, tick, length):
        super(Tap, self).__init__(lane, tick, length)

        self.add(Color(rgb=[0.5, 0.5, 1], a=0.8))
        self.width = 20
        self.height = 100
        self.x -= self.width/2
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def on_update(self, dt):
        pass


class Bomb(Target):
    """
    Targets that users will destroy by firing a bomb.
    """

    def __init__(self, lane, tick, length):
        super(Bomb, self).__init__(lane, tick, length)

        self.destroyed_with = "rocket"

        self.add(Color(rgb=[1, 0.5, 0.5], a=0.8))
        self.radius = 50
        self.x -= self.radius/2 # TODO refine this because IDK
        #self.x += self.length
        self.y -= self.radius/2
        self.shape = Ellipse(pos=(self.x, self.y), size=(self.radius, self.radius))
        self.add(self.shape)

    def on_update(self, dt):
        pass


class Hold(Target):
    """
    Targets that the user will destroy by holding the laser.
    """

    def __init__(self, lane, tick, length):
        super(Hold, self).__init__(lane, tick, length)

        # TODO investigate the x coordinate in-depth
        self.add(Color(rgb=[0.5, 1, 0.5], a=0.8))
        self.width = self.length * PIXELS_PER_TICK
        self.height = 120
        #self.x -= self.width/2
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def on_update(self, dt):
        pass


class GameDisplay(InstructionGroup):

    def __init__(self, song_data):
        super(GameDisplay, self).__init__()

        self.tempo_map = TempoMap(data=song_data['tempo'])
        self.targets = []
        self.beats = []
        self.t = 0
        
        self.scroll = Translate(0, 0)
        
        # Add non-scrolling visuals

        # ship
        self.ship = Spaceship(SPACESHIP_X, 360)
        self.add(self.ship)

        # TODO improve ship's x and y position so laser comes out of ship instead of inside
        self.beam = Beam(self.ship.x, self.ship.y)
        self.add(self.beam)

        # TODO: separate object
        self.add(Color(rgb=[0.9,0.9,0.9]))
        
        self.add(Line(width = 1, points=[0, 360 - 80 - 160, 1280, 360 - 80 - 160]))
        self.add(Color(rgb=[0.3,0.3,0.3]))
        self.add(Line(width = 1, points=[0, 360 - 80, 1280, 360 - 80]))
        self.add(Line(width = 1, points=[2, 360 + 80, 1280, 360 + 80]))
        self.add(Color(rgb=[0.9,0.9,0.9]))
        self.add(Line(width = 1, points=[2, 360 + 80 + 160, 1280, 360 + 80 + 160]))
        self.add(NowPillar())
        
        self.add(self.scroll)
        # Add scrolling visuals
        for beat in song_data['beats']:
            self.add_beat_line(beat)
            
        for target in song_data['targets']:
            self.add_target(target)
            
    def hit_target(self, target):
        self.targets.remove(target)
        self.remove(target)

    def add_target(self, target_data):
        target_dict = {'tap': Tap, 'bomb': Bomb, 'hold': Hold}
        kind, lane, tick, length = target_data
        target = target_dict[kind](lane, tick, length)
        self.targets.append(target)
        self.add(target)
    
    def add_beat_line(self, beat_data):
        count, tick, length = beat_data
        beat = BeatLine(count, tick)
        self.beats.append(beat)
        self.add(beat)

    def set_aim(self, aim):
        self.beam.set_aim(aim)
        # TODO improve ship y position
        self.beam.update_points(self.ship.y)

    def get_targets_in_range(self, start_tick, end_tick):
        """
        Gets all of the targets within a tick range
        """
        return filter(lambda x: x.in_tick_range(start_tick, end_tick), self.targets)
    
    def on_update(self, dt):
        pass
        # self.t += dt
        # tick = self.tempo_map.time_to_tick(self.t)
        
        # self.scroll.x = - tick * PIXELS_PER_TICK
        
    def set_scroll(self, time):
        
        self.scroll.x = - self.tempo_map.time_to_tick(time) * PIXELS_PER_TICK
     


