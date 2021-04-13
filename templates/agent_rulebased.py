import random
import sys
import numpy as np
sys.path.append("..")
from bombots.environment import Bombots
from collections import Counter

class RuleBasedAgent:
    
    # Feel free to remove the comments from this file, they 
    # can be found in the source on GitHub at any time

    # https://github.com/CogitoNTNU/bombots

    # This is an example agent that can be used as a learning resource or as 
    # a technical base for your own agents. There are few limitations to how 
    # this should be structured, but the functions '__init__' and 'act' need
    # to have the exact parameters that they have in the original source.

    # Action reference:
    # Bombots.NOP    - No Operation
    # Bombots.UP     - Move up 
    # Bombots.DOWN   - Move down
    # Bombots.LEFT   - Move left
    # Bombots.RIGHT  - Move right
    # Bombots.BOMB   - Place bomb

    # State reference: 
    # env_state['agent_pos'] - Coordinates of the controlled bot - (x, y) tuple
    # env_state['enemy_pos'] - Coordinates of the opponent bot   - (x, y) tuple
    # env_state['bomb_pos']  - List of bomb coordinates          - [(x, y), (x, y)] list of tuples
    
    def __init__(self, env):
        self.env = env

    def act(self, env_state):
        smart_moves = []

        # Get agent coordinates from dictionary
        x, y = env_state['self_pos']

        # Combine box map and wall map into one collision matrix (as both are solid)
        solid_map = np.logical_or(self.env.box_map, self.env.wall_map)
        
        # Check for collisions in neighboring tiles
        if x + 1 in range(0, self.env.w) and solid_map[x + 1][y] == 0: smart_moves.append(Bombots.RIGHT)
        if x - 1 in range(0, self.env.w) and solid_map[x - 1][y] == 0: smart_moves.append(Bombots.LEFT)
        if y + 1 in range(0, self.env.h) and solid_map[x][y + 1] == 0: smart_moves.append(Bombots.DOWN)
        if y - 1 in range(0, self.env.h) and solid_map[x][y - 1] == 0: smart_moves.append(Bombots.UP)

        # If standing on a bomb [Just an example, not used here]
        if env_state['self_pos'] in env_state['bomb_pos']:
            pass
        
        # If possible, consider bombing
        if env_state['ammo'] > 0: 
            smart_moves.append(Bombots.BOMB)

        # Choose randomly among the actions that seem relevant
        if len(smart_moves) > 0:
            action = random.choice(smart_moves) 
        else: action = Bombots.NOP
        
        return action