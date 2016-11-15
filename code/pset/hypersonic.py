import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        
    def on_key_down(self, keycode, modifiers):
        pass
        
    def on_key_up(self, keycode):
        pass
        
    def on_update(self) :    
       pass

run(MainWidget)