
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from common.clock import *

SPACESHIP_X = 100
NOW_X = 300
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
        self.add(Color(rgb=[0.2, 0.2, 0.8]))
        self.rect = Rectangle(pos=(self.x-80, self.y-40), size=(140,80))
        self.add(self.rect)
        
        self.add(Color(rgb=[1.0, 1.0, 1.0]))
        self.cursor_rect = Rectangle(pos=[NOW_X - 20 - 5, self.y - 50], size=[10, 100])
        self.add(self.cursor_rect)

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
        self.cursor_rect.pos = (NOW_X - 20 - 5, self.y-50)

    def on_update(self, dt):
        pass

class HealthBar(InstructionGroup):
    """
    Health bar for the ship, saying its fuel level
    """
    def __init__(self):
        super(HealthBar, self).__init__()
        self.x_base = 375
        self.y_base = 620

        self.outside_rect = Rectangle(pos=(self.x_base, 620), size=(400,60))
        self.add(self.outside_rect)

        self.add(Color(rgb=[0.5, 0.0, 0.0]))
        self.inner_rect = Rectangle(pos=(self.x_base+2, self.y_base+1), size=(200, 58))
        self.add(self.inner_rect)

    def update_health(self, value):
        # TODO make it scale at different rates at different points maybe?
        x_val = int(396.*value/100)
        self.inner_rect.size = (x_val, 58)

    def on_update(self, dt):
        pass

class NowPillar(InstructionGroup):
    """
    The pillar that the user needs to hit objects with the laser.
    """

    def __init__(self):
        super(NowPillar, self).__init__()
        self.add(Color(rgb=[0.4, 0.2, 0.2]))
        self.add(Line(width=4, points=[NOW_X - 20, 360 - 80 - 160, NOW_X - 20, 360 + 80 + 160]))

    def on_update(self, dt):
        pass


class BeatLine(InstructionGroup):
    """
    Lines that go along with the beat to help the user follow the beat.
    """
    def __init__(self, count, tick):
        super(BeatLine, self).__init__()

        self.add(Color(rgb=[0.35, 0.35, 0.35], a=0.8))
        x = NOW_X + tick * PIXELS_PER_TICK
        width = 3 if count == 1 else 1
        self.add(Line(width=width, points=[x, 360 - 80 - 160, x, 360 + 80 + 160]))


class Target(InstructionGroup):
    """
    Abstract class for characteristics common among all types of
    targets that the user will fire at.
    """

    def __init__(self, lane, tick):
        super(Target, self).__init__()
        self.lane = lane
        self.tick = tick
        self.x = NOW_X + tick * PIXELS_PER_TICK
        self.y = self.vertical_pos_from_lane(lane)
        self.is_hit = False


    def destroy(self):
        pass

    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick


    def vertical_pos_from_lane(self, lane):
        if lane == 'top':
            return 360 + 160
        elif lane == 'mid':
            return 360
        else:
            return 360 - 160

    def hit(self):
        pass 
        
    def miss(self):
        pass
        
    def on_update(self, dt):
        pass


class Tap(Target):
    """
    Targets that the user will destroy with a single laser.
    """

    def __init__(self, lane, tick):
        super(Tap, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 20
        self.height = 50
        self.x -= self.width/2
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (100, False)
    
    def on_update(self, dt):
        pass


class HoldStart(Target):
    def __init__(self, lane, tick):
        super(HoldStart, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 120
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (100, True)
        
    def on_update(self, dt):
        pass
        
class Hold(Target):
    """
    Targets that the user will destroy by holding the laser.
    """

    def __init__(self, lane, tick):
        super(Hold, self).__init__(lane, tick)

        # TODO investigate the x coordinate in-depth
        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 30
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, False)
        
    def on_update(self, dt):
        pass
        
        
class HoldEnd(Target):
    def __init__(self, lane, tick):
        super(HoldEnd, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 30
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, True)
        

        
    def on_update(self, dt):
        pass
        
class ReverseStart(Target):
    def __init__(self, lane, tick):
        super(ReverseStart, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 120
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (100, True)
        
    def on_update(self, dt):
        pass
        
class Reverse(Target):
    """
    Targets that the user will destroy by holding the laser.
    """

    def __init__(self, lane, tick):
        super(Reverse, self).__init__(lane, tick)

        # TODO investigate the x coordinate in-depth
        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 30
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, False)
        
    def on_update(self, dt):
        pass
        
        
class ReverseEnd(Target):
    def __init__(self, lane, tick):
        super(ReverseEnd, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 30
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, True)
        
    def on_update(self, dt):
        pass
        
# TODO: object-oriented rating: 4/10 not enough polymorphism
class Gate(InstructionGroup):

    def __init__(self, pos, tick):
        super(Gate, self).__init__()
        self.pos = pos
        self.tick = tick
        self.x = NOW_X + tick * PIXELS_PER_TICK
        self.y = 360 - 240 + 480 * (pos)
        self.is_hit = False

        self.color = Color(rgb=[1.0, 1.0, 1.0], a=0.9)
        self.add(self.color)
        self.width = 40 * PIXELS_PER_TICK
        self.height = 20
        self.shape = Rectangle(pos=(self.x, self.y - 0.5 * self.height), size=(self.width, self.height))
        self.add(self.shape)

    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick

    def hit(self):
        pass 
        
    def miss(self):
        pass
        
    def on_update(self, dt):
        pass
        
class Trail(InstructionGroup):

    def __init__(self, pos, tick):
        super(Trail, self).__init__()
        self.pos = pos
        self.tick = tick
        self.x = NOW_X + tick * PIXELS_PER_TICK
        self.y = 360 - 240 + 480 * (pos)
        self.is_hit = False
        
        self.color = Color(rgb=[1.0, 1.0, 1.0], a=0.9)
        self.add(self.color)
        self.width = 40 * PIXELS_PER_TICK
        self.height = 20
        self.shape = Rectangle(pos=(self.x, self.y - 0.5 * self.height), size=(self.width, self.height))
        self.add(self.shape)

    def destroy(self):
        pass

    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick

    def hit(self):
        pass 
        
    def miss(self):
        pass
        
    def on_update(self, dt):
        pass

class GameDisplay(InstructionGroup):

    def __init__(self, song_data):
        super(GameDisplay, self).__init__()

        self.tempo_map = TempoMap(data=song_data['tempo'])
        self.targets = [] # taps and hold_start
        self.passive_targets = [] # hold and hold_end
        self.traces = []
        self.beats = []
        self.t = 0
        
        self.scroll = Translate(0, 0)
        
        # Health Bar
        self.health = HealthBar()
        self.add(self.health)

        # TODO: separate object
        self.add(Color(rgb=[0.9,0.9,0.9]))
        
        self.add(Line(width = 1, points=[0, 360 - 80 - 160, 1280, 360 - 80 - 160]))
        self.add(Color(rgb=[0.3,0.3,0.3]))
        self.add(Line(width = 1, points=[0, 360 - 80, 1280, 360 - 80]))
        self.add(Line(width = 1, points=[2, 360 + 80, 1280, 360 + 80]))
        self.add(Color(rgb=[0.9,0.9,0.9]))
        self.add(Line(width = 1, points=[2, 360 + 80 + 160, 1280, 360 + 80 + 160]))
        self.add(NowPillar())
        
        
        
        
        # Apply scrolling screen
        self.add(PushMatrix())
        self.add(self.scroll)
        # Add scrolling visuals
        for beat in song_data['beats']:
            self.add_beat_line(beat)
            
        for trace in song_data['traces']:
            self.add_trace(trace)
          
        for passive in song_data['passive_targets']:
            self.add_passive_target(passive)
            
        for target in song_data['targets']:
            self.add_target(target)
        self.add(PopMatrix())    
        
        # ship
        self.ship = Spaceship(SPACESHIP_X, 360)
        self.add(self.ship)
            
    def hit_target(self, target):
        return target.hit()
        
    def miss_target(self, target):
        target.miss()

    def add_target(self, target_data):
        target_dict = {'tap': Tap, 'hold_start': HoldStart, 'reverse_start': ReverseStart }
        kind, lane, tick = target_data
        target = target_dict[kind](lane, tick)
        self.targets.append(target)
        self.add(target)
        
    def add_passive_target(self, target_data):
        target_dict = {'hold': Hold, 'hold_end': HoldEnd, 'reverse': Reverse, 'reverse_end': ReverseEnd}
        kind, lane, tick = target_data
        target = target_dict[kind](lane, tick)
        self.passive_targets.append(target)
        self.add(target)
        
    def add_trace(self, trace_data):
        kind, pos, tick = trace_data
        trace = { 'gate' : Gate, 'trail' : Trail }[kind](pos, tick)
        self.traces.append(trace)
        self.add(trace)
    
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
        return filter(lambda x: x.in_tick_range(start_tick, end_tick) and not x.is_hit, self.targets)
    
    def get_passive_targets_in_range(self, start_tick, end_tick):
        return filter(lambda x: x.in_tick_range(start_tick, end_tick) and not x.is_hit, self.passive_targets)
    
    def on_update(self, dt):
        pass
        # self.t += dt
        # tick = self.tempo_map.time_to_tick(self.t)
        
        # self.scroll.x = - tick * PIXELS_PER_TICK
        
    def set_scroll(self, time):
        
        self.scroll.x = - self.tempo_map.time_to_tick(time) * PIXELS_PER_TICK
     


