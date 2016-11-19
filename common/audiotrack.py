#####################################################################
#
# audiotrack.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from song import *
from wavegen import *
from audio import kSamplingRate

# audio track - very simple wrapper around wavegen
class AudioTrack(Track):
   def __init__(self, audio, filepath):
      super(AudioTrack, self).__init__()
      self.wavegen = WaveFileGenerator(filepath)
      self.wavegen.stop()
      audio.add_generator(self.wavegen)

   def start(self):
      print 'audio start'
      self.wavegen.start()

   def stop(self):
      print 'audio stop'
      self.wavegen.stop()

   def set_time(self, time):
      self.wavegen.set_pos(time * kSamplingRate)

   def set_mute(self, mute):
      if mute:
         self.wavegen.set_gain(0)
      else:
         self.wavegen.set_gain(1)