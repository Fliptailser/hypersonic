class Spaceship(InstructionGroup):

	def __init__(self):
        super(Spaceship, self).__init__()

    def on_update(self, dt):
    	pass


class NowPillar(InstructionGroup):

	def __init__(self):
        super(NowPillar, self).__init__()

    def on_update(self, dt):
    	pass


class Laser(InstructionGroup):

	def __init__(self):
        super(Laser, self).__init__()

    def on_update(self, dt):
    	pass


class Rocket(InstructionGroup):

	def __init__(self):
        super(Rocket, self).__init__()

    def on_update(self, dt):
    	pass


class Beam(InstructionGroup):

	def __init__(self):
        super(Beam, self).__init__()

    def on_update(self, dt):
    	pass


class Target(InstructionGroup):

	def __init__(self, lane, tick, length):
        super(Target, self).__init__()
        self.lane = lane
        self.tick = tick
        self.length = length

    def on_update(self, dt):
    	pass


class Tap(Target):

	def __init__(self, lane, tick, length):
        super(Tap, self).__init__(lane, tick, length)

    def on_update(self, dt):
    	pass


class Bomb(Target):

	def __init__(self, lane, tick, length):
        super(Bomb, self).__init__(lane, tick, length)

    def on_update(self, dt):
    	pass


class Hold(Target):

	def __init__(self, lane, tick, length):
        super(Hold, self).__init__(lane, tick, length)

    def on_update(self, dt):
    	pass


class GameDisplay(InstructionGroup):

	def __init__(self, targets_list):
        super(GameDisplay, self).__init__()

        target_dict = {'tap': Tap, 'bomb': Bomb, 'hold': Hold}
        self.targets = []

        for t in targets_list:
        	kind, lane, tick, length = t
        	target = target_dict[kind](lane, tick, length)
        	self.targets.append(target)

    def on_update(self, dt):
    	pass







