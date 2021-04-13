from environment.bombots import Bombots
from templates.agent_rl import RLAgent

# For Travis
import sys
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

agents = [RLAgent(env), RLAgent(env)]

if '--test' not in sys.argv:
    states  = env.reset()
    rewards = [0, 0]
    done    = False
    info    = {}

    while True:
        states, rewards, done, info = env.step([agents[i].act(states[i], rewards[i], done, info) for i in range(len(agents))])
        
        env.render() # Comment out this call to train faster
        
        if done: states = env.reset()