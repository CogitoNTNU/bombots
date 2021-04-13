
from environment.bombots import Bombots

import numpy as np
import pygame as pg
import random
import sys
from examples.agent_random import RandomAgent
from examples.agent_rulebased import RuleBasedAgent


if '--novid' in sys.argv: 
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

env = Bombots(scale=64, framerate=5, state_mode=Bombots.STATE_DICT)

agent_a = RuleBasedAgent(env)
agent_b = RandomAgent(env)

if '--test' not in sys.argv:
    states = env.reset()
    
    state_a = states[0]
    state_b = states[1]
    
    while True:
        states, rewards, done, info = env.step([agent_a.act(state_a), agent_b.act(state_b)])
        env.render()
        
        if done: 
            states = env.reset()
    
            state_a = states[0]
            state_b = states[1]