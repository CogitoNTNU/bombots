import random
import sys
import numpy as np
from bombots.environment import Bombots

sys.path.append("..")

class RuleBasedAgent_0:

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
 #   def openPath( int, width):
  #      counter = 0
   #     if bot_x + 1 in range(0, self.env.width) and solid_map[bot_x + 1][bot_y] == 0:
    
    def bombDanger(self, x, y, env_state):
        radiusMe = self.env.bbots[1].str + 1
        radiusEnemy =  self.env.bbots[0].str + 1
        for bomb in self.env.bombs: 
            if bomb.instigator == env_state['self_ref']:
                if abs(x - bomb.pos_x) <= radiusMe and y == bomb.pos_y or abs(y - bomb.pos_y) <= radiusMe and x == bomb.pos_x:
                    return True
                elif  self.env.fire_map[x][y] == 1:
                    return True
            else:
                if abs(x-bomb.pos_x) <= radiusEnemy and y == bomb.pos_y or abs(y-bomb.pos_y) <= radiusEnemy and x == bomb.pos_x:
                    return True
                elif  self.env.fire_map[x][y] == 1:
                    return True
        return False

     #   distanceEnemyBomb = regne ut minste distanse fra bombe self skal være til alle tider
     #   distanceMyBomb = 
        
    #    if env_state['bomb_pos']:

        # Størrelse på bombespreng til motstander: (self.env.bbots[1].str)
        #Bomb_pos; aldri være rett ved siden av en bombe, sjekke upgrades /.str til motspiller for å se om d cool å være to ruter ifra
        #.str = størrelse på eksplosjon, .ammo = ammostørrelse
        #env.fire_map = 1, betyr det er fire i den ruten
    def getEnemy(self, x, y):
        if x == self.env.bbots[0].pos_x and y == self.env.bbots[0].pos_y:
            enemy = self.env.bbots[1]
        elif x == self.env.bbots[1].pos_x and y == self.env.bbots[1].pos_y:
            enemy = self.env.bbots[0]
        return enemy

    def chooseAction(self, x, y, env_state, smart_moves):
        if (x + 1 < self.env.width and self.env.box_map[x+1][y] == 1) or (x - 1 < self.env.width and self.env.box_map[x-1][y] == 1) or (y + 1 < self.env.width and self.env.box_map[x][y+1] == 1) or (y - 1 < self.env.width and self.env.box_map[x][y-1] == 1):
            if env_state['ammo'] > 0: return Bombots.BOMB
        return random.choice(smart_moves)
       

    def act(self, env_state):
        smart_moves = []

        # Get agent coordinates from dictionary
        bot_x, bot_y = env_state['self_pos']

        #Get enemy player
        enemy = self.getEnemy(bot_x, bot_y)

        #Vectors for where to go next, 
        goLeft = 0
        LEFT = False
        goRight = 0
        RIGHT = False
        goUp = 0
        UP = False
        goDown = 0
        DOWN = False
        boolean = [LEFT, RIGHT, UP, DOWN]
        # Combine box map and wall map into one collision matrix (as both are solid)
        solid_map = np.logical_or(self.env.box_map, self.env.wall_map)
        # Check for collisions in neighboring tiles
        # Check rightSide
        if bot_x + 1 < self.env.width and solid_map[bot_x + 1][bot_y] == 0 and self.env.fire_map[bot_x +1][bot_y] != 1:
            RIGHT = True
        if bot_x - 1 in range(0, self.env.width) and solid_map[bot_x - 1][bot_y] == 0 and self.env.fire_map[bot_x - 1][bot_y] != 1:
            LEFT = True
        if bot_y + 1 in range(0, self.env.height) and solid_map[bot_x][bot_y + 1] == 0 and self.env.fire_map[bot_x][bot_y +1] != 1:
            DOWN = True
        if bot_y - 1 in range(0, self.env.height) and solid_map[bot_x][bot_y - 1] == 0 and self.env.fire_map[bot_x][bot_y -1] != 1:
            UP = True


        if RIGHT:
            if not self.bombDanger(bot_x + 1, bot_y, env_state) or self.bombDanger(bot_x, bot_y, env_state):
                goRight += 2
                smart_moves.append(Bombots.RIGHT)
        
        if LEFT:
            if not self.bombDanger(bot_x - 1, bot_y, env_state) or self.bombDanger(bot_x, bot_y, env_state):
                smart_moves.append(Bombots.LEFT)
                goLeft += 2
     
        if DOWN:
            if not self.bombDanger(bot_x , bot_y + 1, env_state) or self.bombDanger(bot_x, bot_y, env_state):
                smart_moves.append(Bombots.DOWN)
                goDown += 2
     
        if UP:
            if not self.bombDanger(bot_x, bot_y -1, env_state) or self.bombDanger(bot_x, bot_y, env_state):
                smart_moves.append(Bombots.UP)
                goUp += 2
  
           
        # If possible, consider bombing
  #      if env_state['ammo'] > 0:
   #         smart_moves.append(Bombots.BOMB)
    
        # Choose randomly among the actions that seem relevant
        if smart_moves:  
            action = self.chooseAction(bot_x, bot_y, env_state, smart_moves)
        else: action = Bombots.NOP

        return action
