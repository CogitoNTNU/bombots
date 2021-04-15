import sys
import pygame as pg
from bombots.environment import Bombots
from templates.agent_random import RandomAgent
from templates.agent_rulebased import RuleBasedAgent

# For Travis
if '--novid' in sys.argv:
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

def main():
    cell_scale = 16
    pg.init()

    # Initialize the master window
    screen = pg.display.set_mode((cell_scale * 12 * 4, cell_scale * 12 * 4))

    envs = [Bombots(
        # Size of game tiles (in pixels), of each individual game
        scale=cell_scale,
        # Frames per second, set this to 0 for unbounded framerate
        framerate=0,
        # Useful printing during execution
        verbose=True,
        # This is required to render multiple environments in the same window
        standalone=False,
        # For rule-based agents
        state_mode=Bombots.STATE_DICT
    ) for _ in range(4 * 4)]

    agents_a = [RuleBasedAgent(env) for env in envs]
    agents_b = [RandomAgent(env) for env in envs]

    if '--test' not in sys.argv:
        states = [env.reset() for env in envs]

        while True:
            for i, env in enumerate(envs):

                states[i], _, done, _ = env.step([agents_a[i].act(states[i][0]),
                                                  agents_b[i].act(states[i][1])])

                env.render()

                # Paste each individual environment surface into the master window
                screen.blit(env.screen, ((i % 4) * (env.width + 1) * env.scale,
                                         (i // 4) * (env.height + 1) * env.scale))

                if done:
                    states[i] = env.reset()

if __name__ == '__main__':
    main()
