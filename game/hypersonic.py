import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.clock import *
from common.gfxutil import *
from common.kivyparticle import *
from kivy.core.window import Window
from ConfigParser import ConfigParser

import parse
import display
from audioctrl import AudioController
from player import *

from kivy.clock import Clock as kivyClock

SONG_NAMES = [ 'DanimalCannon_Behemoth', 'PROTODOME_ThisIsBLUESHIFT' , 'DaftPunk_HBFS', 'DanimalCannon_Axis']

SONG_DICT = {'DanimalCannon_Behemoth': 'Danimal Cannon - Behemoth', 'DanimalCannon_Axis': 'Danimal Cannon - Axis',
             'PROTODOME_ThisIsBLUESHIFT': 'PROTODOME - This is BLUESHIFT',
             'DaftPunk_HBFS': 'Daft Punk - Harder, Better, Faster, Stronger'}


class MainWidget(BaseWidget) :
    def __init__(self, song_name, audio_ctrl, highscore, level_callback, menu_callback, score_callback):
        super(MainWidget, self).__init__()

        self.song_name = song_name
        self.audio_ctrl = audio_ctrl
        self.highscore = highscore
        self.level_callback = level_callback
        self.menu_callback = menu_callback
        self.score_callback = score_callback
        
        print('Loading MIDI...')
        midi_lists = parse.parse_MIDI_chart(song_name)
        #print midi_lists

        # midi_lists['beats']: list of (beat_number, tick,  beat_length)
        # midi_lists['signals']: TODO
        # midi_lists['targets']: list of (type, lane, tick, length)
        # midi_lists['tempo']: list of (time, tick)
        
        self.score_label = Label(text = str(0), halign='right', font_size=50, x = 940, y = 600, texture_size=[400,200])
        self.streak_label = Label(text = "Streak: 0", halign='right', font_size=25, x = 1100, y = 620, texture_size=[400,200])
        self.multiplier_label = Label(text = "Multiplier: 1x", halign='right', font_size=25, x = 1100, y = 590, texture_size=[400,200])
        self.add_widget(self.score_label)
        self.add_widget(self.streak_label)
        self.add_widget(self.multiplier_label)

        # set up particle system for thrusters
        self.ps_top = ParticleSystem('../particle/particle.pex')
        self.ps_bottom = ParticleSystem('../particle/particle.pex')
        self.ps_on = False
        self.add_widget(self.ps_top)
        self.add_widget(self.ps_bottom)

        # make explosion on the ship
        self.explosion = ParticleSystem('../explosion/particle.pex')
        self.explosion.exploding_particles = 5
        self.explosion.start()
        self.explosion_on = False  # used for the ship exploding at the end

        song_path = '../assets/' + song_name + '.wav'
        self.audio_ctrl.set_song(song_path, midi_lists['tempo'])

        self.tempo_map = TempoMap(data=midi_lists['tempo'])
        self.display_objects = AnimGroup()
        self.game_display = display.GameDisplay(midi_lists, self.ps_top, self.ps_bottom, self.explosion)
        self.display_objects.add(self.game_display)
        self.player = Player(midi_lists, self.game_display, self.audio_ctrl)

        # pause menu
        self.pause_labels = [Label(text="", font_size=30, halign='left') for i in xrange(3)]
        self.pause_menu = display.PauseMenu(self.pause_labels)
        self.display_objects.add(self.pause_menu)

        # level end menu
        self.end_labels = [Label(text="", font_size=30, halign='left') for i in xrange(2)]
        score_label2 = Label(text="", font_size=30, halign='left')
        self.level_end_menu = display.LevelEndMenu(self.end_labels, score_label2, self.player)
        self.display_objects.add(self.level_end_menu)

        self.canvas.add(self.display_objects)

        self.paused = True

        self.start_label = Label(text="Press Start to Go!", font_size=100, x=700, y=300, halign='left')
        self.add_widget(self.start_label)
        if not self.controller_found:
            self.start_label.text = "Press the\nspacebar\nto Go!"

        self.xbox_buttons = {0: "dpad_up", 1: "dpad_down", 2: "dpad_left", 3: "dpad_right",
                             4: "start", 5: "back", 8: "LB", 9: "RB",
                             11: "A", 12: "B", 13: "X", 14: "Y",
                             7: "right_joy", 6: "left_joy"}

        self.left_joystick_y = 0

        self.started = False
        self.ended = False
        self.toggle_ps()

        # need explosion to be on top
        self.add_widget(self.explosion)

        # add labels last so that they can appear on windows
        self.add_widget(score_label2)
        map(self.add_widget, self.pause_labels)
        map(self.add_widget, self.end_labels)
        
        
    def key_down(self, keycode, modifiers):
        
        if keycode[1] == 'spacebar' and not self.ended:
            self.audio_ctrl.toggle()
            self.paused = not self.paused
            if not self.started:
                self.remove_widget(self.start_label)
            self.started = True

            if self.paused:
                self.pause_menu.appear()
            elif not self.ended:
                self.pause_menu.disappear()

        if not self.paused:
            if keycode[1] in 'qwertyuiop':
                self.player.fire('top', keycode[1])
                
            if keycode[1] in 'asdfghjkl':
                self.player.fire('mid', keycode[1])
                
            if keycode[1] in 'zxcvbnm':
                self.player.fire('bot', keycode[1])
        
    def key_up(self, keycode):
        if not self.paused:
            if keycode[1] in 'qwertyyuiop':
                self.player.release('top', keycode[1])
                
            if keycode[1] in 'asdfghjkl':
                self.player.release('mid', keycode[1])
                
            if keycode[1] in 'zxcvbnm':
                self.player.release('bot', keycode[1])

    def touch_down(self, touch):
        # TODO figure out how to update mouse config so doesn't make the circles on right clicks
        # print touch.button
        if self.paused and self.ended:
            action = self.level_end_menu.get_selected_name()

            if action in ['Retry', "Fly again!"]:
                self.level_callback(self.song_name)
            elif action == 'Quit':
                self.menu_callback()
        elif self.paused:
            action = self.pause_menu.get_selected_name()
            if action == 'Resume':
                self.joy_button_down(4)  # pretend start was pressed
            elif action == 'Restart':
                self.level_callback(self.song_name)
            elif action == 'Quit':
                self.menu_callback()

    def touch_up(self, touch):
        pass

    def joy_button_down(self, buttonid):
        """
        XBOX controller buttons down
        """
        # print "down", buttonid
        try:
            button = self.xbox_buttons[buttonid]
        except:
            # ERROR: button can't be found
            return

        if button == 'start' and not self.ended:
            self.audio_ctrl.toggle()
            self.paused = not self.paused
            if not self.started:
                self.remove_widget(self.start_label)
            self.started = True

            if self.paused:
                self.pause_menu.appear()
            else:
                self.pause_menu.disappear()

        if not self.paused:
            if button == 'Y':
                self.player.fire('top', button)
                
            if button in ['X', 'B']:
                self.player.fire('mid', button)
                
            if button == 'A':
                self.player.fire('bot', button)

        # level end menu
        if self.paused and self.ended:
            if button == 'dpad_down':
                self.level_end_menu.move_selection_down()

            if button == 'dpad_up':
                self.level_end_menu.move_selection_up()

            if button == 'A':
                action = self.level_end_menu.get_selected_name()

                if action in ['Retry', "Fly again!"]:
                    self.level_callback(self.song_name)
                elif action == 'Quit':
                    self.menu_callback()

        # pause menu
        elif self.paused:
            if button == 'dpad_down':
                self.pause_menu.move_selection_down()

            if button == 'dpad_up':
                self.pause_menu.move_selection_up()

            if button == 'A':
                action = self.pause_menu.get_selected_name()

                if action == 'Resume':
                    self.joy_button_down(4)  # pretend start was pressed
                elif action == 'Restart':
                    self.level_callback(self.song_name)
                elif action == 'Quit':
                    self.menu_callback()


    def joy_button_up(self, buttonid):
        """
        XBOX controller buttons up
        """
        # print "up", buttonid
        try:
            button = self.xbox_buttons[buttonid]
        except:
            # button can't be found
            return
        if not self.paused:
            if button == 'Y':
                self.player.release('top', button)
                
            if button in ['X', 'B']:
                self.player.release('mid', button)
                
            if button == 'A':
                self.player.release('bot', button)

    def joy_axis(self, axis_id, value):
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

    def toggle_ps(self):
        self.ps_on = not self.ps_on
        if self.ps_on:
            self.ps_top.start()
            self.ps_bottom.start()
        else:
            self.ps_top.stop()
            self.ps_bottom.stop()
        
    def update(self):
        self.score_label.text = str(self.player.score)
        self.streak_label.text = "Streak: " + str(self.player.streak)
        self.multiplier_label.text = "Multiplier: " + str(self.player.streak_multiplier) + "x"
        self.audio_ctrl.on_update()

        if not self.paused:
            self.display_objects.on_update()
            self.game_display.set_scroll(self.audio_ctrl.get_time())

            # move with left joystick
            if self.controller_found:
                # get rid of slight unintentional movement by making a threshold it needs to hit
                if abs(self.left_joystick_y) < 0.2:
                    self.left_joystick_y = 0
                self.player.joystick_move(self.left_joystick_y)
            # move with the mouse
            else:
                self.player.update_position(Window.mouse_pos)
                
            self.player.on_update()
        elif not self.ended and self.started and not self.controller_found:
            self.pause_menu.select(Window.mouse_pos)

        if self.game_display.reach_end(self.audio_ctrl.get_time()) and not self.ended:
            # player won
            new_highscore = self.score_callback(self.song_name, self.player.score)
            self.level_end_menu.appear(new_highscore)
            self.paused = True
            self.ended = True

        if not self.ended and self.player.health == 0:
            # player died
            new_highscore = self.score_callback(self.song_name, self.player.score)
            self.level_end_menu.appear(new_highscore)
            self.paused = True
            self.ended = True
            self.game_display.remove(self.game_display.ship)
            self.explosion.stop()
            self.ps_top.stop()
            self.ps_bottom.stop()
            self.explosion_on = True
            # remove the beams
            self.game_display.release_beams('top')
            self.game_display.release_beams('mid')
            self.game_display.release_beams('bot')

        if self.ended and not self.controller_found:
            self.level_end_menu.select(Window.mouse_pos)


class MenuWidget(BaseWidget) :
    def __init__(self, callback, scores):
        super(MenuWidget, self).__init__()
        self.main_label = Label(text = "Hypersonic", halign='right', font_size=100, x = Window.width/2, y = 550)
        self.add_widget(self.main_label)

        self.delay = 10
        self.callback = callback
        self.scores = scores

        self.levels = SONG_NAMES
        self.display_objects = AnimGroup()
        
        labels = [Label(text="", font_size='30sp', halign='left') for i in xrange(3)]

        self.preview_display = display.PreviewDisplay(self.levels, labels, SONG_DICT, self.scores)
        self.display_objects.add(self.preview_display)

        self.previews = self.preview_display.get_previews()

        self.canvas.add(self.display_objects)

        self.selected = -1

        for label in labels:
            self.add_widget(label)

        self.xbox_buttons = {0: "dpad_up", 1: "dpad_down", 2: "dpad_left", 3: "dpad_right",
                             4: "start", 5: "back", 8: "LB", 9: "RB",
                             11: "A", 12: "B", 13: "X", 14: "Y",
                             7: "right_joy", 6: "left_joy"}

    def update_highscores(self, scores):
        """
        Updates the highscores
        """
        self.scores = scores
        self.preview_display.update_highscores(scores)

    def joy_axis(self, axis_id, value):
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
        if axis_id == 1 and abs(value) > 0.75 and self.delay >= 15:
            # negative value positive percent is down
            if value < 0:
                self.select_up()
            else:
                self.select_down()
            # delay so has to press more than once to make it move a lot
            self.delay = 0

        if axis_id == 0 and abs(value) > 0.75 and self.delay >= 15:
            # negative value positive percent is down
            if value > 0:
                self.previews = self.preview_display.scroll('right')
                self.selected = -1
            else:
                self.previews = self.preview_display.scroll('left')
                self.selected = -1
            # delay so has to press more than once to make it move a lot
            self.delay = 0 

    def select_down(self):
        try:
            self.previews[self.selected].unhighlight()
        except:
            pass        

        self.selected += 1
        if self.selected == len(self.previews):
            self.selected = -1

        if self.selected != -1:
            self.previews[self.selected].highlight()

    def select_up(self):

        try:
            self.previews[self.selected].unhighlight()
        except:
            pass

        self.selected -= 1
        if self.selected == -2:
            self.selected = len(self.previews)-1

        if self.selected != -1:
            self.previews[self.selected].highlight()

    def touch_down(self, touch):
        # TODO figure out how to update mouse config so doesn't make the circles on right clicks
        # print touch.button
        self.start_level() # handles if logic in function to see if startable

        direction = self.preview_display.check_triangle_highlighted(touch.pos)
        self.previews = self.preview_display.scroll(direction)
        if direction != "none":
            self.selected = -1

    def joy_button_down(self, buttonid):
        """
        XBOX controller buttons down
        """
        # print "down", buttonid
        try:
            button = self.xbox_buttons[buttonid]
        except:
            # ERROR: button can't be found
            return

        if button in ['A', 'start']:
            self.start_level()  # handles if logic to see if startable

        if button == 'dpad_down':
            self.select_down()
        elif button == 'dpad_up':
            self.select_up()
        elif button == 'dpad_right':
            self.previews = self.preview_display.scroll('right')
            self.selected = -1
        elif button == 'dpad_left':
            self.previews = self.preview_display.scroll('left')
            self.selected = -1

    def start_level(self):
        """
        Starts the selected level
        """
        if 0 <= self.selected < len(self.levels):
            self.callback(self.previews[self.selected].level_name)

    def update(self):
        (x,y) = Window.mouse_pos
        self.preview_display.check_triangle_highlighted(Window.mouse_pos)

        found_selection = False

        if not self.controller_found:
            for i, preview in enumerate(self.previews):
                is_highlighted = preview.is_highlighted(x, y)
                if is_highlighted:
                    self.selected = i
                    found_selection = True

            if not found_selection:
                self.selected = -1

        self.delay += 1
        if self.delay > 100:
            self.delay = 15 # keep small number so doesn't take up too much memory

        # make sure no selected errors
        if not (-1 <= self.selected < len(self.previews)):
            self.selected = -1  # just unselect if problem...


class FatherWidget(BaseWidget):
    """
    Handles moving between main widgets that are displayed
    """
    def __init__(self):
        super(FatherWidget, self).__init__()

        self.scores = read_highscores()

        self.menu = MenuWidget(self.start_new_level, self.scores)
        self.add_widget(self.menu)
        self.current_widget = self.menu

        self.audio_ctrl = AudioController()

    # make it so only ONE widget can accept input. disabling them didn't work for whatever reason
    def on_key_down(self, keycode, modifiers):
        try:
            self.current_widget.key_down(keycode, modifiers)
        except AttributeError, e:
            pass

    def on_key_up(self, keycode):
        try:
            self.current_widget.key_up(keycode)
        except AttributeError, e:
            pass

    def on_touch_down(self, touch):
        try:
            self.current_widget.touch_down(touch)
        except AttributeError, e:
            pass


    def on_touch_up(self, touch):
        try:
            self.current_widget.touch_up(touch)
        except AttributeError, e:
            pass

    def on_joy_button_down(self, buttonid):
        try:
            self.current_widget.joy_button_down(buttonid)
        except AttributeError, e:
            pass

    def on_joy_button_up(self, buttonid):
        try:
            self.current_widget.joy_button_up(buttonid)
        except AttributeError, e:
            pass

    def on_joy_axis(self, axis_id, value):
        try:
            self.current_widget.joy_axis(axis_id, value)
        except AttributeError, e:
            pass

    def on_update(self):
        try:
            self.current_widget.update()
        except AttributeError, e:
            pass

    def start_new_level(self, song_name):
        self.remove_widget(self.current_widget)
        if self.current_widget != self.menu:
            del self.current_widget
        self.current_widget = MainWidget(song_name, self.audio_ctrl, self.scores[song_name],
                                         self.start_new_level, self.return_to_menu, self.check_highscore)
        self.add_widget(self.current_widget)

    def return_to_menu(self):
        self.remove_widget(self.current_widget)
        self.current_widget = self.menu
        self.add_widget(self.current_widget)

    def check_highscore(self, song, score):
        if self.scores[song] < score:
            self.scores[song] = score
            self.menu.update_highscores(self.scores)
            return True
        return False

    def on_close(self):
        """
        Update highscores.txt when the widget closes
        """
        write_highscores(self.scores)


def read_highscores():
    scores = {}
    with open('highscores.txt', 'r') as f:
        for line in f:
            try:
                line = line.split()
                name, score = line[0], int(line[1])
                if name in scores and score > scores[name] or name not in scores:
                    scores[name] = score
            except:
                pass
    return scores

def write_highscores(scores):
    with open('highscores.txt', 'w') as f:
        for song, score in scores.iteritems():
            f.write(song + " " + str(score) + "\n")


Window.size = (1280, 720)

run(FatherWidget)