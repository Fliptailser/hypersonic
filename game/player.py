class Player(object):
    def __init__(self, midi_data, display, audio_ctrl):
        super(Player, self).__init__()
        # player characteristics
        self.health = 50
        self.max_streak = 0
        self.streak = 0
        self.score = 0
        self.aim = 'mid'
        self.holding_laser = False

        # objects to be able to do cool stuff
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.beats = midi_data['beats']
        # self.targets = display.get_targets()  # TODO in display

    def gain_health(amt=1):
        self.health += amt
        if self.health > 100:
            self.health = 100

    def lose_health(amt=1):
        self.health -= amt
        if self.health < 0:
            self.health = 0

    def get_health():
        return self.health

    def aim_top():
        self.aim = 'top'
        # self.display.set_aim(self.aim)  # TODO in display

    def aim_bottom():
        self.aim = 'bot'
        # self.display.set_aim(self.aim)  # TODO in display

    def release_aim():
        self.aim = 'mid'
        # self.display.set_aim(self.aim)  # TODO in display

    # called by MainWidget
    def fire_laser():
        hit_target()
        self.holding_laser = True
        pass

    # called by MainWidget
    def release_laser():
        # TODO need to check if too early
        self.holding_laser = False
        pass

    # called by MainWidget
    def fire_rocket():
        hit_target(is_laser=False)
        pass

    def hit_target(is_laser=True):
        """
        Determines if the current shot hit one of the targets
        """
        
        pass

    def on_update(self):
        # TODO
        pass
