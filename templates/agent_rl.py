import random
import sys
sys.path.append("..")

class RLAgent:
    def __init__(self, env):
        # Reference to the environment to get info such as board dimensions 
        # or action space, modifying the properties of this object is not legal 
        # and will result in a disqualification
        self.env = env

    def act(self, state, reward, done, info):
        return self.env.action_space.sample()