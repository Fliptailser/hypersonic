#####################################################################
#
# song.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from clock import *
from wavegen import *

# defines a thing that can play and will be managed by class Song
class Track(object):
   def __init__(self):
      self.song = None

   # keep a reference to the song
   def set_song(self, song):
      self.song = song

   # set position of track
   def set_time(self, time):
      pass

   def start(self):
      pass

   def stop(self):
      pass


# groups together a clock, conductor, scheduler, and tracks, along with
# shuttle controls
class Song(object):
   def __init__(self):
      super(Song, self).__init__()
      self.clock = Clock()
      self.cond = Conductor(self.clock)
      self.sched = Scheduler(self.cond)
      self.tracks = []

   def on_update(self):
      self.sched.on_update()

   def add_track(self, track):
      track.set_song(self)
      self.tracks.append(track)

   def set_time(self, time):
      self.clock.set_time(time)
      for t in self.tracks:
         t.set_time(time)

   def start(self):
      self.clock.start()
      for t in self.tracks: 
         t.start()

   def stop(self):
      self.clock.stop()
      for t in self.tracks:
         t.stop()

   def toggle(self):
      if self.clock.is_paused():
         self.start()
      else:
         self.stop()
