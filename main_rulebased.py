import sys
from bombots.environment import Bombots
from templates.agent_random import RandomAgent
from templates.agent_rulebased import RuleBasedAgent
from templates.rulebasedAgent_0 import RuleBasedAgent_0
from templates.rulebasedAgent_1 import RuleBasedAgent_1

if '--novid' in sys.argv:
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

def main():
    env = Bombots(
        # Size of game tiles (in pixels)
        scale=64,
        # Frames per second, set this to 0 for unbounded framerate
        framerate=10,
        # So the state is returned as a dictionary
        state_mode=Bombots.STATE_DICT,
        # Useful printing during execution
        verbose=True,
        # Change this to Bombots.NO_RENDER if you remove the render call
        render_mode=Bombots.RENDER_GFX_RGB
    )

    agents = [RuleBasedAgent_0(env), RuleBasedAgent_1(env)]

    if '--test' not in sys.argv:
        states = env.reset()

        while True:
            states, _, done, _ = env.step([agents[i].act(states[i]) for i in range(len(agents))])

            env.render() # Comment out this call to train faster

            if done:
                states = env.reset()

if __name__ == '__main__':
    main()
