from common.audio import *
from common.song import *
from common.clock import *


class AudioController(object):
    """
    Creates the Audio driver
    Creates a song and loads it with solo and bg audio tracks
    Creates snippets for audio sound fx
    """
    def __init__(self, song_path, song_tempo):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.gain = 0.4
        self.sound_effect_path = 'TODO'

        # create Audio components
        self.song = Song()
        self.tempo_map = TempoMap(data=song_tempo)
        self.song.cond.set_tempo_map(self.tempo_map)

        # add track
        self.song_track = AudioTrack(song_path)
        self.song.add_track(self.song_track)

        self.audio.set_generator(self.song)


    # start / stop the song
    def toggle(self):
        self.song.toggle()

    # mute / unmute the solo track
    def set_mute(self, mute):
        # TODO see if we need
        pass

    # play a sound-fx (miss sound)
    def play_sfx(self):
        # TODO maybe an explosion sound
        pass

    # needed to update audio
    def on_update(self):
        self.audio.on_update()


def midi_beat_to_tempo_beat(beat_list):
    """
    Converts list of (beat_number, tick,  beat_length)
    => (time, tick)
    """
    pass