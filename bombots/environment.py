import gym
import numpy as np
import pygame as pg
import random
import sys

from gym import spaces
from collections import deque
from .texman import TexMan

# - - - - - - - - - - - - - - - - \
# Tensor state, shape=(5, h, w)   |
# - - - - - - - - - - - - - - - - |
# Layer 0: Your position          |
# Layer 1: Other bot positions    |
# Layer 2: Bomb positions         |
# Layer 3: Fire positions         |
# Layer 4: Box positions          |
# Layer 5: Wall position          |
# - - - - - - - - - - - - - - - - /

class Bombots(gym.Env):
    NOP, UP, DOWN, LEFT, RIGHT, BOMB = range(6)
    NO_RENDER, RENDER_GFX_RGB, RENDER_GFX_GRAY, RENDER_SIMPLE = range(4)
    STATE_IMG, STATE_DICT, STATE_TENSOR = range(3)

    def __init__(self, dimensions=(11, 11), render_mode=RENDER_GFX_RGB, state_mode=STATE_TENSOR,
                 framerate=20, scale=32, show_fps=False, standalone=True, verbose=True):

        start_pos = [(1, 1), (9, 9)]

        # Environment configuration
        self.dimensions = dimensions # w, h
        self.width, self.height = dimensions # for cleaner code :)
        self.start_pos = start_pos
        self.random_seed = 0
        self.n_frames = 0
        self.verbose = verbose

        # Object management
        self.bbots = [Bombot(self, start_pos[i], i + 1) for i in range(len(start_pos))] # Object list
        self.bombs = [] # Object list
        self.fires = [] # Object list
        self.upers = [] # Object list
        self.killbuf_bomb = [] # Object destruction buffer
        self.killbuf_fire = [] # Object destruction buffer
        self.killbuf_upg  = [] # Object destruction buffer

        # Map generation
        self.generate_map()

        # Stats
        self.stats = {
            'player1' : {
                'wins' : 0,
                'boxes' : 0,
                'bombs' : 0,
                'upgrades' : 0
            },
            'player2' : {
                'wins' : 0,
                'boxes' : 0,
                'bombs' : 0,
                'upgrades' : 0
            }
        }

        # RL
        self.action_space = spaces.Discrete(6)
        self.state_mode = state_mode
        self.state_function = list([None, self.get_state_dict, self.get_state_tensor])[self.state_mode] 

        # Rendering
        self.scale         = scale # pixels per square
        self.buf_frametime = deque((1, 1), maxlen=100)
        self.framerate     = framerate # frames per second (0 = no cap)
        self.render_mode   = render_mode # 0 = no rendering, 1 = normal rendering, 2 = reduced rendering etc.
        self.show_fps      = show_fps
        
        # Pygame setup
        if self.render_mode != self.NO_RENDER:  
            if standalone:
                pg.init()
                self.screen = pg.display.set_mode((self.dimensions[0] * self.scale, self.dimensions[1] * self.scale))
            else:
                self.screen = pg.Surface((self.dimensions[0] * self.scale, self.dimensions[1] * self.scale))
                
            self.clock = pg.time.Clock()
            self.tm = TexMan(self.scale)
            self.font = pg.font.Font(pg.font.get_default_font(), 16)

    def step(self, action):
        done = False
        
        self.n_frames += 1
        if self.n_frames > 1500:
            self.n_frames = 0
            done = True

        # Clear dynamic maps
        self.fire_map = np.zeros(self.dimensions)

        # Pygame event handling (resolves some crashing)
        if self.render_mode != self.NO_RENDER:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            pg.event.pump()

        # Apply actions
        for i in range(len(self.bbots)):
            bot = self.bbots[i]
            bot.act(action[i])
            for upg in self.upers:
                if bot.x == upg.x and bot.y == upg.y:
                    if upg.upgrade_type == Upgrade.AMMO:
                        bot.ammo += 1
                    if upg.upgrade_type == Upgrade.STR:
                        bot.str += 1
                    self.stats['player{}'.format(bot.id)]['upgrades'] += 1
                    self.killbuf_upg.append(upg)

        # object tick
        for fire in self.fires: # Tick fire before bombs, to allow fire triggering bombs (as the firemap is cleared every tick)
            fire.tick()
        for bomb in self.bombs:
            bomb.tick()
        
        # killbuffer processing
        for bomb in self.killbuf_bomb:
            self.bombs.remove(bomb)
        self.killbuf_bomb.clear()
        
        for fire in self.killbuf_fire:
            self.fires.remove(fire)
        self.killbuf_fire.clear()
        
        for upg in self.killbuf_upg:
            if upg in self.upers: 
                self.upers.remove(upg)
        self.killbuf_upg.clear()
        
        # Check for death

        for i in range(len(self.bbots)):
            if self.fire_map[self.bbots[i].x][self.bbots[i].y] == 1:
                self.stats['player{}'.format(((i + 1) % 2) + 1)]['wins'] += 1
                self.bbots[i].dead = True
                done = True

                if self.verbose: print('Player {} wins!'.format(((i + 1) % 2) + 1))

        # Setup return values

        states = [self.state_function(bot) for bot in self.bbots]
        rewards = [0 if not done else -1 if bot.dead else 1 for bot in self.bbots]
        info = self.stats

        return states, rewards, done, info
    
    def get_state_tensor(self, bot):
        tensor = np.zeros((6, self.width, self.height))
        tensor[0][bot.x][bot.y] = 1
        
        for obot in self.bbots:
            if obot != bot:
                tensor[1][obot.x][obot.y] = 1
        
        for bomb in self.bombs:
            tensor[2][bomb.x][bomb.y] = 1
            
        tensor[3] = np.copy(self.fire_map)
        tensor[4] = np.copy(self.box_map)
        tensor[5] = np.copy(self.wall_map)

        return tensor

    def get_state_dict(self, bot):
        state = {}
        
        state['self_pos'] = (bot.x, bot.y)
        state['ammo'] = bot.ammo
        state['opponent_pos'] = [(obot.x, obot.y) for obot in filter(lambda x : x != bot, self.bbots)]
        state['bomb_pos'] = [(bomb.x, bomb.y) for bomb in self.bombs]
        
        return state

    def reset(self):
        self.bbots = [Bombot(self, self.start_pos[i], i + 1) for i in range(len(self.start_pos))] # Object list
        self.bombs = [] # Object list
        self.fires = [] # Object list
        self.upers = [] # Object list

        self.generate_map()
        
        states = [self.state_function(bot) for bot in self.bbots]
        
        return states

    def generate_map(self, seed=0):
        self.wall_map = np.zeros(self.dimensions) # walls
        self.box_map = np.zeros(self.dimensions)
        self.fire_map = np.zeros(self.dimensions)
        
        random.seed(seed)

        start_area = [pos for pos in self.start_pos]
        for pos in self.start_pos:
            i, j = pos
            start_area.extend([(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)])
        
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if i % 2 == 0 and j % 2 == 0:
                    self.wall_map[i][j] = 1
                elif random.randint(0, 1) == 0 and (i, j) not in start_area:
                    self.box_map[i][j] = 1
                elif random.randint(0, 4) == 0 and (i, j) not in start_area:
                    self.upers.append(Upgrade(self, (i, j), random.randint(0, 1)))

    def render(self, mode='human'):
        if self.render_mode != self.NO_RENDER:
            # Base color
            pg.draw.rect(self.screen, (24, 24, 24), (0, 0, self.dimensions[0] * self.scale, self.dimensions[1] * self.scale))
            
            for i in range(self.dimensions[0]):
                for j in range(self.dimensions[1]):
                    # Wall
                    if self.wall_map[i][j] == 1:
                        self.screen.blit(self.tm.spr_wall, (self.scale * i, self.scale * j, self.scale, self.scale))
                    # Floor
                    else:
                        self.screen.blit(self.tm.spr_floor, (self.scale * i, self.scale * j, self.scale, self.scale))
                    # Box
                    if self.box_map[i][j] == 1:
                        self.screen.blit(self.tm.spr_box, (self.scale * i, self.scale * j, self.scale, self.scale))
                    
                    # Fire
                    if self.fire_map[i][j] == 1:
                        f_bstr = self.get_neighbors(i, j, self.fire_map)
                        
                        fspr_key = 'x'
                        
                        # Ends
                        if f_bstr == (1, 0, 0, 0): fspr_key = 'w'
                        if f_bstr == (0, 1, 0, 0): fspr_key = 'e'
                        if f_bstr == (0, 0, 1, 0): fspr_key = 'n'
                        if f_bstr == (0, 0, 0, 1): fspr_key = 's'
                        
                        # Beams
                        if f_bstr == (1, 1, 0, 0): fspr_key = 'h'
                        if f_bstr == (0, 0, 1, 1): fspr_key = 'v'
                        
                        self.screen.blit(self.tm.spr_fire[fspr_key], (self.scale * i, self.scale * j, self.scale, self.scale))
            
            # Bombs
            for bomb in self.bombs:
                self.screen.blit(self.tm.spr_bomb[3 - (bomb.fuse // 8)], (self.scale * bomb.x, self.scale * bomb.y, self.scale, self.scale))
            
            # Upgrade
            for upg in self.upers:
                self.screen.blit(self.tm.spr_pop_num if upg.upgrade_type == Upgrade.AMMO else self.tm.spr_pop_ext, (self.scale * upg.x, self.scale * upg.y, self.scale, self.scale))

            # Bots
            bot = self.bbots[0]
            if bot.face == Bombot.FACE_N: self.screen.blit(self.tm.spr_bot['green']['n'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_S: self.screen.blit(self.tm.spr_bot['green']['s'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_E: self.screen.blit(self.tm.spr_bot['green']['e'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_W: self.screen.blit(self.tm.spr_bot['green']['w'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            
            # Forgive the horrible code here [TODO: Make this nice]
            bot = self.bbots[1]
            if bot.face == Bombot.FACE_N: self.screen.blit(self.tm.spr_bot['yellow']['n'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_S: self.screen.blit(self.tm.spr_bot['yellow']['s'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_E: self.screen.blit(self.tm.spr_bot['yellow']['e'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            if bot.face == Bombot.FACE_W: self.screen.blit(self.tm.spr_bot['yellow']['w'], (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
            
            # Overlays
            if self.show_fps:
                fps = 1000 // (sum(list(self.buf_frametime)) / len(list(self.buf_frametime)))
                text_surface = self.font.render('FPS: {}'.format(fps), True, (255, 0, 0))
                self.screen.blit(text_surface, dest=(self.scale * self.width - text_surface.get_width() - 8, 8))
                text_surface2 = self.font.render('Stats: {} - {}'.format(self.stats['player1']['wins'], self.stats['player2']['wins']), True, (255, 0, 0))
                self.screen.blit(text_surface2, dest=(self.scale * self.width - text_surface2.get_width() - 8, 32))
            
            pg.display.flip()
            self.buf_frametime.append(self.clock.tick(int(self.framerate)))
        else:
            raise RuntimeError('Render function was called with render_mode=Bombots.NO_RENDER. Resolve this either by removing the call or change render mode.')

    def get_neighbors(self, x, y, cmap):
        right = x + 1 in range(0, self.width) and cmap[x + 1][y]
        left  = x - 1 in range(0, self.width) and cmap[x - 1][y]
        down  = y + 1 in range(0, self.height) and cmap[x][y + 1]
        up    = y - 1 in range(0, self.height) and cmap[x][y - 1]
        return right, left, down, up

class Bombot:
    FACE_N, FACE_S, FACE_E, FACE_W = range(4)
    
    def __init__(self, env, spawn_location, id):
        self.x, self.y = spawn_location # (i, j) = (x, y), [x][y]
        self.ammo = 1
        self.str = 1
        self.env = env
        self.face = Bombot.FACE_S
        self.dead = False
        self.id = id

    def act(self, action):
        # Movement
        if action == Bombots.UP:
            if self.y - 1 in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y - 1] == 0 and self.env.box_map[self.x][self.y - 1] == 0:
                self.y -= 1
            self.face = Bombot.FACE_N
            
        if action == Bombots.DOWN:
            if self.y + 1 in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y + 1] == 0 and self.env.box_map[self.x][self.y + 1] == 0:
                self.y += 1
            self.face = Bombot.FACE_S

        if action == Bombots.LEFT:
            if self.x - 1 in range(self.env.dimensions[0]) and self.env.wall_map[self.x - 1][self.y] == 0 and self.env.box_map[self.x - 1][self.y] == 0:
                self.x -= 1
            self.face = Bombot.FACE_W
        
        if action == Bombots.RIGHT:
            if self.x + 1 in range(self.env.dimensions[0]) and self.env.wall_map[self.x + 1][self.y] == 0 and self.env.box_map[self.x + 1][self.y] == 0:
                self.x += 1
            self.face = Bombot.FACE_E
        # Bombing
        if action == Bombots.BOMB:
            if self.ammo > 0:
                self.ammo -= 1
                self.env.bombs.append(Bomb(self.env, self))

class Bomb:
    def __init__(self, env, instigator):
        self.env = env
        self.instigator = instigator
        self.fuse = 30
        self.str = self.instigator.str
        self.x, self.y = (instigator.x, instigator.y)
        env.stats['player{}'.format(instigator.id)]['bombs'] += 1

    def tick(self):
        self.fuse -= 1
        if self.env.fire_map[self.x][self.y] == 1:
            self.fuse = 0
        if self.fuse == 0:
            self.instigator.ammo += 1
            self.env.killbuf_bomb.append(self)
            self.env.fires.append(Fire(self.env, self, (self.x, self.y)))

class Fire:
    def __init__(self, env, instigator, position):
        self.env = env
        self.size = instigator.str
        self.life = 5
        self.x, self.y = position
        self.fire_pos = [(self.x, self.y)]
        
        for i in range(1, self.size + 1):
            if self.x + i in range(self.env.dimensions[0]) and self.env.wall_map[self.x + i][self.y] == 0:
                self.fire_pos.append((self.x + i, self.y))
                if self.env.box_map[self.x + i][self.y] == 1:
                    self.env.box_map[self.x + i][self.y] = 0
                    env.stats['player{}'.format(instigator.instigator.id)]['boxes'] += 1
                    break
            else:
                break

        for i in range(1, self.size + 1):
            if self.x - i in range(self.env.dimensions[0]) and self.env.wall_map[self.x - i][self.y] == 0:
                self.fire_pos.append((self.x - i, self.y))
                if self.env.box_map[self.x - i][self.y] == 1:
                    self.env.box_map[self.x - i][self.y] = 0
                    env.stats['player{}'.format(instigator.instigator.id)]['boxes'] += 1
                    break
            else: 
                break

        for i in range(1, self.size + 1):
            if self.y + i in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y + i] == 0:
                self.fire_pos.append((self.x, self.y + i))
                if self.env.box_map[self.x][self.y + i] == 1:
                    self.env.box_map[self.x][self.y + i] = 0
                    env.stats['player{}'.format(instigator.instigator.id)]['boxes'] += 1
                    break
            else: 
                break

        for i in range(1, self.size + 1):
            if self.y - i in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y - i] == 0:
                self.fire_pos.append((self.x, self.y - i))
                if self.env.box_map[self.x][self.y - i] == 1:
                    self.env.box_map[self.x][self.y - i] = 0
                    env.stats['player{}'.format(instigator.instigator.id)]['boxes'] += 1
                    break
            else: 
                break

        for pos in self.fire_pos:
            self.env.fire_map[pos[0]][pos[1]] = 1

    def tick(self):
        self.life -= 1
        if self.life == 0:
            self.env.killbuf_fire.append(self)
        else:
            for pos in self.fire_pos:
                self.env.fire_map[pos[0]][pos[1]] = 1

class Upgrade:
    AMMO, STR = range(2)

    def __init__(self, env, position, upgrade_type):
        self.env = env
        self.x, self.y = position
        self.upgrade_type = upgrade_type
