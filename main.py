
import environment.bombots as bb

import numpy as np
import pygame as pg
import random
import sys
from examples.agent_random import RandomAgent
from agent_template import GeneralAgent


if '--novid' in sys.argv: 
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

env = bb.Bombots(scale=64, framerate=5)

agent_a = GeneralAgent(env)
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