from common.audio import *
from common.song import *
from common.clock import *
from common.mixer import *


class AudioController(object):
    """
    Creates the Audio driver
    Creates a song and loads it with solo and bg audio tracks
    Creates snippets for audio sound fx
    """
    def __init__(self):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.gain = 0.4
        self.sound_effect_path = 'TODO'

        # create Audio components
        self.mixer = Mixer()
        

    def set_song(self, song_path, song_tempo):
        self.tempo_map = TempoMap(data=song_tempo)
        self.song = Song(tempo_map=self.tempo_map)

        # add track
        self.song_track = AudioTrack(self.mixer, song_path)
        self.song.add_track(self.song_track)

        self.audio.set_generator(self.mixer)

    def get_time(self):
        if self.song_track is not None:
            return self.song_track.get_time()

    def get_tick(self):
        if self.tempo_map is not None:
            return self.time_to_tick(self.song_track.get_time())
        
    # start / stop the song
    def toggle(self):
        if self.song is not None:
            self.song.toggle()

    # mute / unmute the solo track
    def set_mute(self, mute):
        # TODO see if we need
        pass

    # play a sound-fx (miss sound)
    def play_sfx(self):
        # TODO maybe an explosion sound
        pass

    def time_to_tick(self, time) :
        if self.tempo_map is not None:
            return self.tempo_map.time_to_tick(time)

    def tick_to_time(self, tick) :
        if self.tempo_map is not None:
            return self.tempo_map.tick_to_time(tick)

    # needed to update audio
    def on_update(self):
        self.audio.on_update()
