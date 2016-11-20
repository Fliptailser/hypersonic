import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.clock import *
from common.gfxutil import *
from kivy.core.window import Window

import parse
import display
from audioctrl import AudioController



from kivy.clock import Clock as kivyClock

PROTOTYPE_SONG = 'DanimalCannon_Axis'
SONG_PATH = '../assets/Danimal_Cannon- Lunaria-01_Axis.wav'

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        
        print('Loading MIDI...')
        midi_lists = parse.parse_MIDI_chart(PROTOTYPE_SONG)
        #print midi_lists
        
        # midi_lists['beats']: list of (beat_number, tick,  beat_length)
        # midi_lists['signals']: TODO
        # midi_lists['targets']: list of (type, lane, tick, length)
        # midi_lists['tempo']: list of (time, tick)

        song_path = '../assets/' + PROTOTYPE_SONG + '.wav'
        self.audio_ctrl = AudioController(song_path, midi_lists['tempo'])

        self.tempo_map = TempoMap(data=midi_lists['tempo'])
        self.display_objects = AnimGroup()
        self.game_display = display.GameDisplay(midi_lists)
        self.display_objects.add(self.game_display)
        self.canvas.add(self.display_objects)
        
        self.paused = True
        
    def on_key_down(self, keycode, modifiers):
        
        if keycode[1] == 'spacebar':
            self.audio_ctrl.toggle()
            self.paused = not self.paused
          
        
    def on_key_up(self, keycode):
        pass
        
    def on_update(self):
        self.audio_ctrl.on_update()
        if not self.paused:
            self.display_objects.on_update()
            self.game_display.set_scroll(self.audio_ctrl.get_time())
            
Window.size = (1280, 720)

run(MainWidget)