import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.clock import *

import parse
import audio

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

PROTOTYPE_SONG = 'DanimalCannon_Axis'
SONG_PATH = 'assets/Danimal Cannon - Lunaria - 01 Axis.wav'

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        
        print('Loading MIDI...')
        midi_lists = parse.parse_MIDI_chart(PROTOTYPE_SONG)
        print midi_lists
        
        # midi_lists['beats']: list of (beat_number, tick,  beat_length)
        # midi_lists['signals']: TODO
        # midi_lists['targets']: list of (type, lane, tick, length)

        # self.audio_ctrl = AudioController(SONG_PATH, midi_lists['beats'])
        
    def on_key_down(self, keycode, modifiers):
        pass
        
    def on_key_up(self, keycode):
        pass
        
    def on_update(self) :    
       pass

run(MainWidget)