import random
import sys
sys.path.append("..")
from environment.bombots import Bombots

class RandomAgent:
    def __init__(self, env):
        self.env = env
        self.actions = [
            Bombots.NOP, 
            Bombots.UP, 
            Bombots.DOWN, 
            Bombots.LEFT, 
            Bombots.RIGHT,
            Bombots.BOMB
        ]

    def act(self, env_state):
        return random.choice(self.actions)