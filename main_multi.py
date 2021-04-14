from bombots.environment import Bombots
from templates.agent_random import RandomAgent
from templates.agent_rulebased import RuleBasedAgent
import pygame as pg

# For Travis
import sys
if '--novid' in sys.argv: 
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

cell_scale = 16
pg.init()

# Initialize the master window
screen = pg.display.set_mode((cell_scale * 12 * 4, cell_scale * 12 * 4))            

envs = [Bombots(
    scale      = cell_scale,        # Size of game tiles (in pixels), of each individual game
    framerate  = 10,                # Frames per second, set this to 0 for unbounded framerate
    verbose    = True,              # Useful printing during execution
    standalone = False,             # This is required to render multiple environments in the same window
    state_mode = Bombots.STATE_DICT # For rule-based agents
) for _ in range(4 * 4)]

agents_a = [RuleBasedAgent(env) for env in envs]
agents_b = [RandomAgent(env) for env in envs]

if '--test' not in sys.argv:
    states = [env.reset() for env in envs]

    while True:
        for i in range(len(envs)):
            env = envs[i]
            
            states[i], rewards, done, info = env.step([agents_a[i].act(states[i][0]), agents_b[i].act(states[i][1])])
            
            env.render()

            # Paste each individual environment surface into the master window
            screen.blit(env.screen, ((i % 4) * (env.width + 1) * env.scale, (i // 4) * (env.height + 1) * env.scale))
            
            if done: states[i] = env.reset()
                