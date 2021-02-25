import gym
import numpy as np
import pygame as pg
import random
from .texman import TexMan

class Bombot:
    FACE_N, FACE_S, FACE_E, FACE_W = range(4)
    
    def __init__(self, env, spawn_location):
        self.x, self.y = spawn_location # (i, j) = (x, y), [x][y]
        self.ammo = 1
        self.env = env
        self.face = Bombot.FACE_S

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
        self.x, self.y = (instigator.x, instigator.y)

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
        self.size = 1
        self.life = 5
        self.x, self.y = position
        self.fire_pos = [(self.x, self.y)]
        
        for i in range(1, self.size + 1):
            if self.x + i in range(self.env.dimensions[0]) and self.env.wall_map[self.x + i][self.y] == 0:
                self.fire_pos.append((self.x + i, self.y))
                if self.env.box_map[self.x + i][self.y] == 1:
                    self.env.box_map[self.x + i][self.y] = 0
                    break
            else:
                break

        for i in range(1, self.size + 1):
            if self.x - i in range(self.env.dimensions[0]) and self.env.wall_map[self.x - i][self.y] == 0:
                self.fire_pos.append((self.x - i, self.y))
                if self.env.box_map[self.x - i][self.y] == 1:
                    self.env.box_map[self.x - i][self.y] = 0
                    break
            else: 
                break

        for i in range(1, self.size + 1):
            if self.y + i in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y + i] == 0:
                self.fire_pos.append((self.x, self.y + i))
                if self.env.box_map[self.x][self.y + i] == 1:
                    self.env.box_map[self.x][self.y + i] = 0
                    break
            else: 
                break

        for i in range(1, self.size + 1):
            if self.y - i in range(self.env.dimensions[1]) and self.env.wall_map[self.x][self.y - i] == 0:
                self.fire_pos.append((self.x, self.y - i))
                if self.env.box_map[self.x][self.y - i] == 1:
                    self.env.box_map[self.x][self.y - i] = 0
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

class Bombots(gym.Env):
    NOP, UP, DOWN, LEFT, RIGHT, BOMB = range(6)
    
    def __init__(self, dimensions=(11, 11), render_mode=1, framerate=20, scale=32, start_pos=[(1, 1), (9, 9)]):
        self.dimensions = dimensions # w, h
        self.scale = scale # pixels per square
        self.framerate = framerate # frames per second (0 = no cap)
        self.render_mode = render_mode # 0 = no rendering, 1 = normal rendering, 2 = reduced rendering etc.
        self.wall_map = np.zeros(self.dimensions) # walls
        self.box_map = np.zeros(self.dimensions)
        self.fire_map = np.zeros(self.dimensions)

        self.bbots = [Bombot(self, pos) for pos in start_pos] # Object list
        self.bombs = [] # Object list
        self.fires = [] # Object list
        self.upers = [] # Object list

        self.killbuf_bomb = [] # Object destruction buffer
        self.killbuf_fire = [] # Object destruction buffer

        start_area = [pos for pos in start_pos]
        for pos in start_pos:
            i, j = pos
            start_area.extend([(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)])
        
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if i % 2 == 0 and j % 2 == 0:
                    self.wall_map[i][j] = 1
                elif random.randint(0, 1) == 0 and (i, j) not in start_area:
                    self.box_map[i][j] = 1

        if self.render:
            pg.init()
            self.screen = pg.display.set_mode((self.dimensions[0] * self.scale, self.dimensions[1] * self.scale))
            self.clock = pg.time.Clock()
            self.tm = TexMan(self.scale)
            #self.spr = pg.image.load('environment/res/bb_sprites.png').convert_alpha()


    def step(self, actions):
        # clearance
        self.fire_map = np.zeros(self.dimensions)

        for i in range(len(self.bbots)):
            self.bbots[i].act(actions[i])

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
        
        state_a = {'agent_pos' : (self.bbots[0].x, self.bbots[0].y), 'enemy_pos' : (self.bbots[1].x, self.bbots[1].y)}
        state_b = {'agent_pos' : (self.bbots[1].x, self.bbots[1].y), 'enemy_pos' : (self.bbots[0].x, self.bbots[0].y)}
        
        bomb_pos = [(bomb.x, bomb.y) for bomb in self.bombs]
        state_a['bomb_pos'] = bomb_pos
        state_b['bomb_pos'] = bomb_pos
        
        return state_a, state_b
        
    def reset(self): # TODO: Make this a real reset function
        state_a = {'agent_pos' : (self.bbots[0].x, self.bbots[0].y), 'enemy_pos' : (self.bbots[1].x, self.bbots[1].y)}
        state_b = {'agent_pos' : (self.bbots[1].x, self.bbots[1].y), 'enemy_pos' : (self.bbots[0].x, self.bbots[0].y)}
        
        bomb_pos = [(bomb.x, bomb.y) for bomb in self.bombs]
        state_a['bomb_pos'] = bomb_pos
        state_b['bomb_pos'] = bomb_pos
        
        return state_a, state_b

    def render(self):
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
                # Fire [TODO: Tiling]
                if self.fire_map[i][j] == 1:
                    self.screen.blit(self.tm.spr_fire_x, (self.scale * i, self.scale * j, self.scale, self.scale))
                
        # Bombs
        for bomb in self.bombs:
            self.screen.blit(self.tm.spr_bomb[3 - (bomb.fuse // 8)], (self.scale * bomb.x, self.scale * bomb.y, self.scale, self.scale))

        # Bots
        bot = self.bbots[0]
        if bot.face == Bombot.FACE_N: self.screen.blit(self.tm.spr_bot1_n, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_S: self.screen.blit(self.tm.spr_bot1_s, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_E: self.screen.blit(self.tm.spr_bot1_e, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_W: self.screen.blit(self.tm.spr_bot1_w, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        
        bot = self.bbots[1]
        if bot.face == Bombot.FACE_N: self.screen.blit(self.tm.spr_bot2_n, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_S: self.screen.blit(self.tm.spr_bot2_s, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_E: self.screen.blit(self.tm.spr_bot2_e, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        if bot.face == Bombot.FACE_W: self.screen.blit(self.tm.spr_bot2_w, (self.scale * bot.x, self.scale * bot.y, self.scale, self.scale))
        
        pg.display.flip()
        self.clock.tick(int(self.framerate))