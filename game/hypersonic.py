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
from player import *


from kivy.clock import Clock as kivyClock

PROTOTYPE_SONG = 'DanimalCannon_Axis'

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

        self.player = Player(midi_lists, self.game_display, self.audio_ctrl)
        
        self.paused = True
        # keeps track of w and x being held so only releases when user releases last pressed
        self.last_key_held = 0
        
    def on_key_down(self, keycode, modifiers):
        
        if keycode[1] == 'spacebar':
            self.audio_ctrl.toggle()
            self.paused = not self.paused

        if keycode[1] == 'w':
        	self.player.aim_top()
        	self.last_key_held = 'w'
        elif keycode[1] == 'x':
        	self.player.aim_bottom()
        	self.last_key_held = 'x'
        elif keycode[1] == 's':
        	self.player.release_aim()
        
    def on_key_up(self, keycode):
       
    	# release aim if let go of last key held
        if keycode[1] == 'w' == self.last_key_held:
        	self.player.release_aim()
        elif keycode[1] == 'x' == self.last_key_held:
        	self.player.release_aim()
        
    def on_update(self):
        self.audio_ctrl.on_update()
        if not self.paused:
            self.display_objects.on_update()
            self.game_display.set_scroll(self.audio_ctrl.get_time())
            
Window.size = (1280, 720)

run(MainWidget)