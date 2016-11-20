#####################################################################
#
# song.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################
from audio import kSampleRate
from clock import *
from wavegen import *
from wavesrc import *

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


# audio track - very simple wrapper around wavegen
class AudioTrack(Track):
    def __init__(self, mixer, filepath):
        super(AudioTrack, self).__init__()
        self.wavegen = WaveGenerator(WaveFile(filepath))
        self.wavegen.pause()
        mixer.add(self.wavegen)

    def start(self):
        print 'audio start'
        self.wavegen.play()

    def stop(self):
        print 'audio stop'
        self.wavegen.pause()

    def get_time(self):
        return self.wavegen.get_time()
        
    def set_time(self, time):
        self.wavegen.set_pos(time * kSampleRate)

    def set_mute(self, mute):
        if mute:
            self.wavegen.set_gain(0)
        else:
            self.wavegen.set_gain(1)


# groups together a clock, conductor, scheduler, and tracks, along with
# shuttle controls
class Song(object):
    def __init__(self, tempo_map=None):
        super(Song, self).__init__()
        self.clock = Clock()
        self.clock.stop()
        self.cond = Conductor(self.clock)
        self.cond.set_tempo_map(tempo_map)
        self.sched = Scheduler(self.clock, self.cond.tempo_map)
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
