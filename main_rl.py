
from environment.bombots import Bombots

import numpy as np
import pygame as pg
import random
import sys
from examples.agent_rl import RLAgent

if '--novid' in sys.argv: 
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

env = Bombots(
    scale       = 64,                    # Size of game tiles (in pixels)
    framerate   = 10,                    # Frames per second, set this to 0 for unbounded framerate
    state_mode  = Bombots.STATE_TENSOR,  # So the state is returned as a tensor
    verbose     = True,                  # Useful printing during execution
    render_mode = Bombots.RENDER_GFX_RGB # Change this to Bombots.NO_RENDER if you remove the render call
)

agent_a = RLAgent(env)
agent_b = RLAgent(env)

if '--test' not in sys.argv:
    states  = env.reset()
    rewards = [0, 0]
    done    = False
    info    = {}

    while True:
        states, rewards, done, info = env.step([
            agent_a.act(states[0], rewards[0], done, info), 
            agent_b.act(states[1], rewards[1], done, info)
        ])
        
        env.render() # Comment out this call to train faster
        
        if done: states = env.reset()