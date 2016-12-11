#####################################################################
#
# core.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################



import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock
import traceback
import pygame
import pygame.locals


class BaseWidget(Widget):
    """Has some common core functionality we want in all
    our apps - handling key up/down, closing the app, and update on every frame.
    The subclass of BaseWidget can optionally define these methods, which will
    get called if defined:
       def on_key_down(self, keycode, modifiers):
       def on_key_up(self, keycode):
       def on_close(self):
       def on_update(self):
    """

    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)

        if hasattr(self.__class__, 'on_init'):
            Clock.schedule_once(self._init, 0)

        # keyboard up / down messages
        self.down_keys = []
        kb = Window.request_keyboard(target=self, callback=None)
        kb.bind(on_key_down=self._key_down)
        kb.bind(on_key_up=self._key_up)

        # get called when app is about to shut down
        if hasattr(self.__class__, 'on_close'):
            Window.bind(on_close=self._close)

        # create a clock to poll us every frame
        if hasattr(self.__class__, 'on_update'):
            Clock.schedule_interval(self._update, 0)

        try:
            # initialize xbox controller
            pygame.joystick.init()

            # get the xbox 360 controller
            for i in xrange(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                if joystick.get_name() == "Wireless 360 Controller":
                    self.joystick = joystick
                    self.xbox = i
                    break

            print self.joystick.get_name() + " was found!"
            self.controller_found = True

            self.num_axes = self.joystick.get_numaxes()

            self.num_buttons = self.joystick.get_numbuttons()

            Window.bind(on_joy_button_down=self._joy_button_down)
            Window.bind(on_joy_button_up=self._joy_button_up)
            Window.bind(on_joy_axis=self._joy_axis)
        except:
            print "no xbox controller found"
            self.controller_found = False

    def get_mouse_pos(self) :
        # due to a bug in Kivy, Window.mouse_pos is not correct for
        # high-def displays. This function accounts for that.
        p = Window.mouse_pos
        return (p[0] * Window._density, p[1] * Window._density)


    def _key_down(self, keyboard, keycode, text, modifiers):
        if not keycode[1] in self.down_keys:
            self.down_keys.append(keycode[1])

            if hasattr(self.__class__, 'on_key_down'):
                self.on_key_down(keycode, modifiers)

    def _key_up(self, keyboard, keycode):
        if keycode[1] in self.down_keys:
            self.down_keys.remove(keycode[1])

            if hasattr(self.__class__, 'on_key_up'):
                self.on_key_up(keycode)

    def _joy_button_down(self, window_obj, stick_id, button_id):
        if stick_id == self.xbox and hasattr(self.__class__, 'on_joy_button_down'):
            self.on_joy_button_down(button_id)

    def _joy_button_up(self, window_obj, stick_id, button_id):
        if stick_id == self.xbox and hasattr(self.__class__, 'on_joy_button_up'):
            self.on_joy_button_up(button_id)

    def _joy_axis(self, window_obj, stick_id, axis_id, value):
        if stick_id == self.xbox and hasattr(self.__class__, 'on_joy_axis'):
            self.on_joy_axis(axis_id, value)

    def _close(self, *args):
        self.on_close()

    def _update(self, dt):
        self.on_update()


# to guarantee a termination/shutdown function being called at the end of the
# app's lifetime, you can register the function by calling register_terminate_func.
# it will get called at the end, even if the app crashed.
g_terminate_funcs = []
def register_terminate_func(f) :
    global g_terminate_funcs
    g_terminate_funcs.append(f)


def run(widget, *args):
    """Pass in a widget, and this will automatically run it. Will also
    call termination functions (g_terminate_funcs) at the end of the run,
    even if it was caused by a program crash
    """

    class MainApp(App):
        def __init__(self, *args):
            super(MainApp, self).__init__()
            self.args = args

        def build(self):
            return widget(*self.args)

    try:
        MainApp(*args).run()
    except:
        traceback.print_exc()

    global g_terminate_funcs
    for t in g_terminate_funcs:
        t()


# returns the nth item in values where n is the index of k in keys.
# ex: lookup('s', 'asdf', (4,5,6,7)) will return 5.
def lookup(k, keys, values) :
    if k in keys:
        idx = keys.index(k)
        return values[idx]
    else:
        return None
