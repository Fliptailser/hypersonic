class Player(object):
    def __init__(self, midi_data, display, audio_ctrl):
        super(Player, self).__init__()
        # player characteristics
        self.health = 50
        self.max_streak = 0
        self.streak = 0
        self.streak_multiplier = 1
        self.score = 0
        self.aim = 'mid'
        self.holding_laser = False

        # objects to be able to do cool stuff
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.beats = midi_data['beats']
        self.targets = display.targets
        
        self.current_holds = []

    def gain_health(self, amt=1):
        self.health += amt
        if self.health > 100:
            self.health = 100

    def lose_health(self, amt=1):
        self.health -= amt
        if self.health < 0:
            self.health = 0

    def get_health(self):
        return self.health

    def aim_top(self):
        self.aim = 'top'
        self.display.set_aim(self.aim)

    def aim_bottom(self):
        self.aim = 'bot'
        self.display.set_aim(self.aim)

    def release_aim(self):
        self.aim = 'mid'
        self.display.set_aim(self.aim)

    def update_position(self, mouse):
        x,y = mouse
        self.display.ship.move_vertical(pos=y)

    def joystick_move(self, emphasis=1):
        """
        Moves the spaceship based on joystick motion
        emphasis: what percent of a full step should be taken (can be pos or neg)
        """
        step = int(15*emphasis)
        self.display.ship.move_vertical(step=step)
        
    def fire(self, lane):
        time = self.audio_ctrl.get_time()
        slop_times = (self.audio_ctrl.time_to_tick(time-0.1), self.audio_ctrl.time_to_tick(time+0.1))
        possible_hits = self.display.get_targets_in_range(slop_times[0], slop_times[1])
  
        for target in possible_hits:
            if target.lane == lane:
                self.display.hit_target(target)
                self.score += 100 * self.streak_multiplier
        
            # if target.destroyed_with == 'laser' and is_laser and self.aim == target.lane:
                # target.destroy()
                # self.display.hit_target(target)
                # print "laser hit"
                # # TODO start note_generation
                # self.score += 100 * self.streak_multiplier
            # elif target.destroyed_with == 'rocket' and not is_laser and self.aim == target.lane:
                # target.destroy()
                # self.display.remove_target(target)
                # print "rocket hit"
                # # TODO start rocket, maybe do callback once hits?
                # self.score += 200 * self.streak_multiplier
        
    def update_keys(self, keys):
        self.keys = keys

    def on_update(self):
        time = self.audio_ctrl.get_time()
        slop_times = (self.audio_ctrl.time_to_tick(time-0.1), self.audio_ctrl.time_to_tick(time+0.1))
        possible_hits = self.display.get_targets_in_range(slop_times[0], slop_times[1])
        #for target in possible_hits:
            
