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

cell_scale = 16
pg.init()

screen = pg.display.set_mode((cell_scale * 12 * 4, cell_scale * 12 * 4))            
envs = [bb.Bombots(scale=cell_scale, framerate=0, standalone=False) for _ in range(4 * 4)]

agents_a = [GeneralAgent(env) for env in envs]
agents_b = [GeneralAgent(env) for env in envs]

if '--test' not in sys.argv:
    states_a = [env.reset()[0] for env in envs]
    states_b = [env.reset()[1] for env in envs]

    while True:
        for i in range(len(envs)):
            env = envs[i]
            states_a[i], states_b[i], done = env.step([agents_a[i].act(states_a[i]), agents_b[i].act(states_b[i])])
            env.render()
            screen.blit(env.screen, ((i % 4) * (env.w + 1) * env.scale, (i // 4) * (env.h + 1) * env.scale))
            if done: 
                state_a, state_b = env.reset()