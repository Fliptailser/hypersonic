
class AudioController(object):
    """
    Creates the Audio driver
    Creates a song and loads it with solo and bg audio tracks
    Creates snippets for audio sound fx
    """
    def __init__(self, song_path, solo_path):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.gain = 0.4
        self.sound_effect_path = 'TODO'

        # create Audio components
        self.mixer = Mixer()
        # TODO other generators

        # add all of them
        self.audio.set_generator(self.mixer)
        # TODO add other generators to mixer

        # for some reason everything plays initially, so just stop it
        self.playing = True
        self.toggle()

    # start / stop the song
    def toggle(self):
        self.playing = not self.playing
        if self.playing:
            # TODO play all gens
            pass
        else:
            # TODO pause all gens
            pass

    # mute / unmute the solo track
    def set_mute(self, mute):
        # TODO see if we need
        pass

    # play a sound-fx (miss sound)
    def play_sfx(self):
        # TODO maybe an explosion sound

    # needed to update audio
    def on_update(self):
        self.audio.on_update()