
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from common.clock import *

SPACESHIP_X = 100
SPACESHIP_WIDTH = 140
SPACESHIP_HEIGHT = 80
SPACESHIP_SRC = 'ship_blank.png'
NOW_X = 300
WINDOW_SIZE = (1280, 720)

# 0.25
PIXELS_PER_TICK = 0.3

class Spaceship(InstructionGroup):
    """
    The spaceship that the user controls.
    """

    def __init__(self, x, y, ps_top, ps_bottom, parent_disp):
        super(Spaceship, self).__init__()
        self.x = x
        self.y = y
        self.max_y = 559
        self.min_y = 161
        self.parent_disp = parent_disp

        self.add(Color(rgb=[1.0, 1.0, 1.0]))  # get rid of blue tint on spaceship
        self.rect = Rectangle(pos=(self.x-SPACESHIP_WIDTH/2, self.y-SPACESHIP_HEIGHT/2), size=(SPACESHIP_WIDTH, SPACESHIP_HEIGHT), source=SPACESHIP_SRC)
        self.add(self.rect)
        
        self.add(Color(rgb=[1.0, 1.0, 1.0]))
        self.cursor_rect = Rectangle(pos=[NOW_X - 20 - 5, self.y - 50], size=[10, 100])
        self.add(self.cursor_rect)

        # particle system stuffs
        self.ps_top = ps_top
        self.ps_bottom = ps_bottom
        self.set_ps_pos()
        self.update_ps_from_health(50)

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

        self.rect.pos = (self.x-SPACESHIP_WIDTH/2, self.y-SPACESHIP_HEIGHT/2)
        self.cursor_rect.pos = (NOW_X - 20 - 5, self.y-50)

        self.set_ps_pos()
        

    # pos from 0.0 to 1.0
    def get_pos(self):
        return (self.y - 120) / 480.0

    def set_ps_pos(self):
        self.ps_top.emitter_x = self.x-20
        self.ps_top.emitter_y = self.y+SPACESHIP_HEIGHT/4  + self.parent_disp.y
        self.ps_bottom.emitter_x = self.x-20 
        self.ps_bottom.emitter_y = self.y-SPACESHIP_HEIGHT/4  + self.parent_disp.y

    def update_ps_from_health(self, health):
        """
        Updates the appearance of the particle system based on health
        """
        percent = min(health/100., 1)
        self.max_particles = int(percent*180+20)
        
    def on_update(self, dt):
        if self.ps_top.max_num_particles < self.max_particles:
            self.ps_top.max_num_particles += 1
            self.ps_bottom.max_num_particles += 1
        elif self.ps_top.max_num_particles > self.max_particles:
            self.ps_top.max_num_particles -= 1
            self.ps_bottom.max_num_particles -= 1


class HealthBar(InstructionGroup):
    """
    Health bar for the ship, saying its fuel level
    """
    def __init__(self):
        super(HealthBar, self).__init__()
        self.x_base = 375
        self.y_base = 620

        # make sure it's white
        self.add(Color(rgb=[1,1,1]))

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
    This is the object that shows which lane the ship is aiming at.
    """

    def __init__(self, ship_x, ship_y, lane='mid', hit=False):
        super(Beam, self).__init__()

        self.ship_x = ship_x
        self.ship_y = ship_y

        self.color = Color(rgb=[0.35, 0.98, 1], a=0.3)        
        self.add(self.color)
        self.set_lane(lane, hit)

        # add red first so that blue is on top
        # self.add(Color(rgb=[1, 0.5, 0.5], a=0.3))
        # self.red_line = Line(points=[ship_x, ship_y, RET_X, self.reticle_y], width=3)
        # self.add(self.red_line)
        width = 1
        if hit:
            width = 3
        
        self.blue_line = Line(points=[ship_x, ship_y, NOW_X - 20, self.now_aim_y], width=width)
        self.add(self.blue_line)
        self.t = 0

    def set_lane(self, lane, hit=False):
        """
        This DOES NOT update update the points
        """
        colors = {'mid': [0.90, 0.11, 0.11],
                  'top': [0.98, 0.89, 0.17],
                  'bot': [0.04, 0.78, 0.33]}

        if hit and lane in colors:
            self.color.rgb = colors[lane]
        else:
            # default bright blue
            self.color.rgb = [0.35, 0.98, 1]

        self.lane = lane
        if lane == 'mid':
            self.now_aim_y = 360
            self.reticle_y = 360
        elif lane == 'top':
            self.now_aim_y = 360 + 160
            self.reticle_y = 360 + 160
        else:
            self.now_aim_y = 360 - 160
            self.reticle_y = 360 - 160

    def update_points(self, ship_y):
        self.ship_y = ship_y
        self.blue_line.points = [self.ship_x, self.ship_y, NOW_X - 20, self.now_aim_y]
        #self.red_line.points = [self.ship_x, ship_y, RET_X, self.reticle_y]

    def on_update(self, dt):
        self.t += dt
        return self.t < 0.1

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
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
    
    def on_update(self, dt):
        pass


class HoldStart(Target):
    def __init__(self, lane, tick):
        super(HoldStart, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 50
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (100, True)
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
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
        self.height = 20
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, False)
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
    def on_update(self, dt):
        pass
        
        
class HoldEnd(Target):
    def __init__(self, lane, tick):
        super(HoldEnd, self).__init__(lane, tick)

        self.color = Color(rgb=[0.5, 0.5, 1], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 20
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, True)
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
    def on_update(self, dt):
        pass
        
class ReverseStart(Target):
    def __init__(self, lane, tick):
        super(ReverseStart, self).__init__(lane, tick)

        self.color = Color(rgb=[1.0, 0.5, 0.5], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 50
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
        self.color = Color(rgb=[1.0, 0.5, 0.5], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 20
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, False)
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
    def on_update(self, dt):
        pass
        
        
class ReverseEnd(Target):
    def __init__(self, lane, tick):
        super(ReverseEnd, self).__init__(lane, tick)

        self.color = Color(rgb=[1.0, 0.5, 0.5], a=0.8)
        self.add(self.color)
        self.width = 80 * PIXELS_PER_TICK
        self.height = 20
        self.y -= self.height/2
        self.shape = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.shape)

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return (10, True)
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
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
        
        self.shape = Rectangle(pos=(-20, -20), size=(40, 40))
        
        self.add(PushMatrix())
        self.add(Translate(self.x, self.y))
        self.add(Rotate(angle=45))
        self.add(self.shape)
        self.add(PopMatrix())

    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return 100
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
        
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
        
        self.shape = Rectangle(pos=(-15, -15), size=(30, 30))
        
        self.add(PushMatrix())
        self.add(Translate(self.x, self.y))
        self.add(Rotate(angle=45))
        self.add(self.shape)
        self.add(PopMatrix())

    def destroy(self):
        pass

    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick

    def hit(self):
        self.color.a = 0
        self.is_hit = True
        return 10
        
    def miss(self):
        self.is_hit = True
        self.color.rgb = [0.5, 0.5, 0.5]
        
    def on_update(self, dt):
        pass
        
class Bump(object):
    def __init__(self, v, tick, callback):
        self.v = v
        self.tick = tick
        self.callback = callback
        self.is_hit = False
        
    def in_tick_range(self, start_tick, end_tick):
        return start_tick < self.tick < end_tick
        
        
    def hit(self):
        self.is_hit = True
        self.callback(self.v / 2.0)
    

class GameDisplay(InstructionGroup):

    def __init__(self, song_data, ps_top, ps_bottom):
        super(GameDisplay, self).__init__()

        self.tempo_map = TempoMap(data=song_data['tempo'])
        self.targets = [] # taps and hold_start
        self.passive_targets = [] # hold and hold_end
        self.signals = []
        self.traces = []
        self.beats = []
        self.beams = []
        self.current_holds = {'top' : None, 'mid' : None, 'bot' : None}
        self.t = 0
        
        for signal in song_data['signals']:
            self.add_signal(signal)
        
        self.scroll = Translate(0, 0)
        self.bump = Translate(0, 0)
        self.bump_target = 0
        
        self.add(self.bump)
        
        
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
        self.ship = Spaceship(SPACESHIP_X, 360, ps_top, ps_bottom, self.bump)
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
        
    def add_signal(self, signal_data):
        kind, v, tick = signal_data
        # todo: sloppy - not generalized
        params = {'bump': (Bump, self.screen_bump)}[kind]
        signal = params[0](v, tick, params[1])
        self.signals.append(signal)

    def screen_bump(self, v):
        self.bump.y = 0
        self.bump_target = v
        
    def fire_beam(self, lane, hit):
        """
        Fires a beam in a direction
        lane: {'top', 'mid', 'bot'} lane of beam
        hit: True if hit something
        """
        offset = 5
        beam = Beam(self.ship.x+SPACESHIP_WIDTH/2-offset, self.ship.y, lane=lane, hit=hit)
        self.add(beam)
        self.beams.append(beam)
        # self.beam.set_aim(aim)
        # TODO improve ship y position
        # self.beam.update_points(self.ship.y)

    def release_beams(self, lane):
        """
        Releases all beams in a specified lane
        """
        for beam in self.beams:
            if beam.lane == lane:
                self.remove(beam)
                self.beams.remove(beam)
                

    def get_targets_in_range(self, start_tick, end_tick):
        """
        Gets all of the targets within a tick range
        """
        return filter(lambda x: x.in_tick_range(start_tick, end_tick) and not x.is_hit, self.targets)
    
    def get_passive_targets_in_range(self, start_tick, end_tick):
        return filter(lambda x: x.in_tick_range(start_tick, end_tick) and not x.is_hit, self.passive_targets)
        
    def get_traces_in_range(self, start_tick, end_tick):
        return filter(lambda x: x.in_tick_range(start_tick, end_tick) and not x.is_hit, self.traces)
    
    def check_signals(self, time):
        trigger_window = (self.tempo_map.time_to_tick(time - 0.1), self.tempo_map.time_to_tick(time))
        for signal in filter(lambda x: x.in_tick_range(*trigger_window) and not x.is_hit, self.signals):
            signal.hit()
    
    def on_update(self, dt):
        self.ship.on_update(dt)

        if self.bump.y < self.bump_target:
            self.bump.y += self.bump_target / 2.
        else:
            self.bump_target = 0
            self.bump.y /= 2
            
        for beam in self.beams:
            beam.on_update(dt)
            beam.update_points(self.ship.y)  # make beam follow the ship

            # TODO see how to improve beam disappearance
            if beam.t > 0.1 and self.current_holds[beam.lane] is None:
                self.remove(beam)
                self.beams.remove(beam)
        # self.t += dt
        # tick = self.tempo_map.time_to_tick(self.t)
        
        # self.scroll.x = - tick * PIXELS_PER_TICK
        
    def set_scroll(self, time):
        
        self.scroll.x = - self.tempo_map.time_to_tick(time) * PIXELS_PER_TICK
     

class LevelPreview(InstructionGroup):

    def __init__(self, x, y, level_name, label):
        super(LevelPreview, self).__init__()

        self.x = x
        self.y = y
        self.level_name = level_name

        self.width = 700
        self.height = 150

        self.color = Color(rgb=(0.3, 0.3, 0.3))
        self.add(self.color)
        # instruction groups
        self.rect = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
        self.add(self.rect)
        src = '../assets/%s.jpg' % level_name

        # check if jpg or png
        try:
            # try open as jpg, if not jpg, must be png
            with open(src) as f:
                pass
        except:
            # if not png, then give up
            src = src[:-4] + '.png'


        self.add(Color(rgb=(1,1,1)))
        self.img = Rectangle(pos=(self.x+10, self.y+10), size=(120, 120), source=src)
        self.add(self.img)

        self.label = label
        self.label.text_size = (self.width - 250, self.height - 70)
        self.label.text = level_name
        self.label.x = self.x + 330
        self.label.y = self.y + 70

    def is_highlighted(self, x, y):
        highlighted = (self.x <= x <= self.x+self.width) and (self.y <= y <= self.y+self.height)

        if highlighted:
            self.highlight()
            return True
        else:
            self.unhighlight()
            return False

    def highlight(self):
        self.color.rgb = (0.3, 0.3, 0.6)

    def unhighlight(self):
        self.color.rgb = (0.3, 0.3, 0.3)


class LevelMenu(InstructionGroup):

    def __init__(self, labels):
        super(LevelMenu, self).__init__()  
        self.labels = labels
        self.selected_label = 0
        self.selected_color = (0,0,0.4,1)
        self.labels[self.selected_label].color = self.selected_color

        for i, label in enumerate(self.labels):
            label.text_size = (400, 50)
            label.x = 580
            label.y = 460-i*70
            print label.color
        
        self.outer_rect_color = Color(rgb=(0.3, 0.3, 0.3))
        self.outer_rect = Rectangle(pos=(380, 160), size=(600, 400))
        

    def move_selection_down(self):
        # TODO select down
        self.labels[self.selected_label].color = (1,1,1, 1)
        self.selected_label = (self.selected_label+1) % len(self.labels)
        self.labels[self.selected_label].color = self.selected_color

    def move_selection_up(self):
        # TODO select up
        self.labels[self.selected_label].color = (1,1,1,1)
        self.selected_label = (self.selected_label+1) % len(self.labels)
        self.labels[self.selected_label].color = self.selected_color

    def select(self, mouse_pos):
        (x, y) = mouse_pos
        # TODO

    def appear(self):
        self.add(self.outer_rect_color)
        self.add(self.outer_rect)
        self.selected_label = 0
        self.labels[self.selected_label].color = self.selected_color
        # in children make sure that the labels actually have text

    def disappear(self):
        self.clear()
        for label in self.labels:
            label.text = ""
            label.color = (1, 1, 1, 1)

    def get_selected_name(self):
        """
        Returns empty string if not visible
        """
        return self.labels[self.selected_label].text

    def on_update(self, dt):
        pass

    # TODO other methods?


class PauseMenu(LevelMenu):

    def __init__(self, labels):
        # labels needs to be 3 labels
        super(PauseMenu, self).__init__(labels)
        

    # TODO other methods
    def appear(self):
        super(PauseMenu, self).appear()
        self.labels[0].text = "Resume"
        self.labels[1].text = "Restart"
        self.labels[2].text = "Quit"

class LevelEndMenu(LevelMenu):

    def __init__(self, labels):
        super(LevelEndMenu, self).__init__(labels)  

    # TODO other methods
    def appear(self):
        super(LevelEndMenu, self).appear()
        self.labels[0].text = "Retry"
        self.labels[1].text = "Quit"




