class Player(object):
    def __init__(self, midi_data, display, audio_ctrl):
        super(Player, self).__init__()
        # player characteristics
        self.health = 50
        self.streak = 0
        self.streak_multiplier = 1
        self.max_streak = 0
        self.score = 0

        # objects to be able to do cool stuff
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.beats = midi_data['beats']
        self.targets = display.targets
        
    def gain_health(self, amt=1.5):
        self.health += amt*min(1, self.streak_multiplier/2)
        if self.health > 100:
            self.health = 100
        self.display.health.update_health(self.health)

    def lose_health(self, amt=1):
        self.health -= amt
        if self.health < 0:
            self.health = 0
        self.display.health.update_health(self.health)

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
        
    def fire(self, lane, keycode):
        
        time = self.audio_ctrl.get_time()
        self.display.fire_beam(lane)
        slop_times = (self.audio_ctrl.time_to_tick(time-0.1), self.audio_ctrl.time_to_tick(time+0.1))
        possible_hits = self.display.get_targets_in_range(slop_times[0], slop_times[1])
        hit = False
  
        points = 0
        for target in possible_hits:
            if target.lane == lane:
                points, hold = self.display.hit_target(target)
                if hold:
                    self.display.current_holds[lane] = keycode
                
                hit = True
                break

        if hit:
            self.gain_health()
            self.streak += 1
            if self.streak > self.max_streak:
                self.max_streak = self.streak
            self.streak_multiplier = int(self.streak/5)+1
            self.score += points * self.streak_multiplier
        else:
            self.display.current_holds[lane] = None
            self.lose_health()
            self.streak = 0
            self.streak_multiplier = 1
        
    def release(self, lane, keycode):
        if self.display.current_holds[lane] == keycode:
            self.display.current_holds[lane] = None
        self.display.release_beams(lane)

    def on_update(self):
        time = self.audio_ctrl.get_time()
        miss_window = (self.audio_ctrl.time_to_tick(time-0.2), self.audio_ctrl.time_to_tick(time-0.1))
        possible_misses = self.display.get_targets_in_range(miss_window[0], miss_window[1])
        for target in possible_misses:
            # TODO: send up penalties for missing
            self.lose_health(amt=1)
            self.streak = 0
            self.streak_multiplier = 1
            self.display.miss_target(target)
            
        possible_misses_holds = self.display.get_passive_targets_in_range(miss_window[0], miss_window[1])
        for target in possible_misses_holds:
            # TODO: send up penalties for missing
            self.lose_health(amt=1)
            self.streak = 0
            self.streak_multiplier = 1
            self.display.miss_target(target)
            
            
        hold_window = (self.audio_ctrl.time_to_tick(time - 0.1), self.audio_ctrl.time_to_tick(time - 0.05))
        for hold in self.display.get_passive_targets_in_range(hold_window[0], hold_window[1]):
            if self.display.current_holds[hold.lane] != None:
                points, end_hold = self.display.hit_target(hold)
                if end_hold:
                    self.display.current_holds[hold.lane] = None
                self.score += points * self.streak_multiplier
            
            