
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from common.clock import *

NOW_X = 250
WINDOW_SIZE = (1280, 720)

# TODO: better scroll speed / fix jittery-looking scrolling
# It has to do with how scrolling is synced to the song frame. It's 100% synced but it gets jittery at high scroll speeds
PIXELS_PER_TICK = 0.15

class Spaceship(InstructionGroup):

    def __init__(self):
        super(Spaceship, self).__init__()

    def on_update(self, dt):
        pass


class NowPillar(InstructionGroup):

    def __init__(self):
        super(NowPillar, self).__init__()
        self.add(Color(rgb=[0.9, 0.9, 0.9]))
        self.add(Line(width=4, points=[NOW_X, 360 - 80 - 160, NOW_X, 360 + 80 + 160]))

    def on_update(self, dt):
        pass
        
class BeatLine(InstructionGroup):
    def __init__(self, count, tick):
        super(BeatLine, self).__init__()

        self.add(Color(rgb=[0.5, 0.5, 0.5], a=0.8))
        x = NOW_X + tick * PIXELS_PER_TICK
        width = 3 if count == 1 else 1
        self.add(Line(width=width, points=[x, 360 - 80 - 160, x, 360 + 80 + 160]))

class Laser(InstructionGroup):

    def __init__(self):
        super(Laser, self).__init__()

    def on_update(self, dt):
        pass


class Rocket(InstructionGroup):

    def __init__(self):
        super(Rocket, self).__init__()

    def on_update(self, dt):
        pass


class Beam(InstructionGroup):

    def __init__(self):
        super(Beam, self).__init__()

    def on_update(self, dt):
        pass


class Target(InstructionGroup):

    def __init__(self, lane, tick, length):
        super(Target, self).__init__()
        self.lane = lane
        self.tick = tick
        self.length = length

    def on_update(self, dt):
        pass


class Tap(Target):

    def __init__(self, lane, tick, length):
        super(Tap, self).__init__(lane, tick, length)

    def on_update(self, dt):
        pass


class Bomb(Target):

    def __init__(self, lane, tick, length):
        super(Bomb, self).__init__(lane, tick, length)

    def on_update(self, dt):
        pass


class Hold(Target):

    def __init__(self, lane, tick, length):
        super(Hold, self).__init__(lane, tick, length)

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
    
    def on_update(self, dt):
        pass
        # self.t += dt
        # tick = self.tempo_map.time_to_tick(self.t)
        
        # self.scroll.x = - tick * PIXELS_PER_TICK
        
    def set_scroll(self, time):
        
        self.scroll.x = - self.tempo_map.time_to_tick(time) * PIXELS_PER_TICK
     



