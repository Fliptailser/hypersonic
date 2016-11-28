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
from ConfigParser import ConfigParser

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
        
        self.label = Label(text = str(0), halign='right', font_size=50, x = 940, y = 600, texture_size=[400,200])
        self.add_widget(self.label)

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
        
        self.key_counts = {'top' : 0, 'mid' : 0, 'bot' : 0}
        
        self.i = 0

        self.xbox_buttons = {0: "dpad_up", 1: "dpad_down", 2: "dpad_left", 3: "dpad_right",
                             4: "start", 5: "back", 8: "LB", 9: "RB",
                             11: "A", 12: "B", 13: "X", 14: "Y"}

        self.left_joystick_y = 0
        
    def on_key_down(self, keycode, modifiers):
        
        if keycode[1] == 'spacebar':
            self.audio_ctrl.toggle()
            self.paused = not self.paused

        if keycode[1] in 'qwertyyuiop':
            self.key_counts['top'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('top')
            
        if keycode[1] in 'asdfghjkl':
            self.key_counts['mid'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('mid')
            
        if keycode[1] in 'zxcvbnm':
            self.key_counts['bot'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('bot')
            
        # if keycode[1] == 'w':
        	# self.player.aim_top()
        	# self.last_key_held = 'w'
        # elif keycode[1] == 's':
        	# self.player.aim_bottom()
        	# self.last_key_held = 's'
        
    def on_key_up(self, keycode):
        if keycode[1] in 'qwertyyuiop':
            self.key_counts['top'] -= 1
            self.player.update_keys(self.key_counts)
            
        if keycode[1] in 'asdfghjkl':
            self.key_counts['mid'] -= 1
            self.player.update_keys(self.key_counts)
            
        if keycode[1] in 'zxcvbnm':
            self.key_counts['bot'] -= 1
            self.player.update_keys(self.key_counts)
            
    	# release aim if let go of last key held
        # if keycode[1] == 'w' == self.last_key_held:
        	# self.player.release_aim()
        # elif keycode[1] == 's' == self.last_key_held:
        	# self.player.release_aim()

    def on_touch_down(self, touch):
        # TODO figure out how to update mouse config so doesn't make the circles on right clicks
        print touch.button

    def on_touch_up(self, touch):
        pass

    def on_joy_button_down(self, buttonid):
        """
        XBOX controller buttons down
        """
        # print "down", buttonid
        button = self.xbox_buttons[buttonid]

        if button == 'start':
            self.audio_ctrl.toggle()
            self.paused = not self.paused

        if button == 'Y':
            self.key_counts['top'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('top')
            
        if button == 'B':
            self.key_counts['mid'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('mid')
            
        if button == 'A':
            self.key_counts['bot'] += 1
            self.player.update_keys(self.key_counts)
            self.player.fire('bot')


    def on_joy_button_up(self, buttonid):
        """
        XBOX controller buttons up
        """
        # print "up", buttonid
        button = self.xbox_buttons[buttonid]
        
        if button == 'Y':
            self.key_counts['top'] -= 1
            self.player.update_keys(self.key_counts)
            
        if button == 'B':
            self.key_counts['mid'] -= 1
            self.player.update_keys(self.key_counts)
            
        if button == 'A':
            self.key_counts['bot'] -= 1
            self.player.update_keys(self.key_counts)

    def on_joy_axis(self, axis_id, value):
        """
        XBOX controller axes changes
        0: left joystick x
        1: left joystick y
        2: right joystick x
        3: right joystick y
        4: left trigger
        5: right trigger
        """
        # print "axis", axis_id, value
        if axis_id == 1:
            # negative value positive percent is down
            self.left_joystick_y = -value
        
    def on_update(self):
        self.label.text = str(self.player.score)
        self.audio_ctrl.on_update()
        print Window.mouse_pos

        if not self.paused:
            self.display_objects.on_update()
            self.game_display.set_scroll(self.audio_ctrl.get_time())

            # move with left joystick
            if self.controller_found:
                self.player.joystick_move(self.left_joystick_y)
            # move with the mouse
            else:
                self.player.update_position(Window.mouse_pos)
                
            self.player.on_update()
            
Window.size = (1280, 720)

run(MainWidget)