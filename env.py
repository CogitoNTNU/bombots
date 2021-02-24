
import numpy as np
import pygame as pg
import random

# TODO: only do this if test flag is passed
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

dimensions = (11, 11) # w, h
scale = 32
framerate = 20

pg.init()
screen = pg.display.set_mode((dimensions[0] * scale, dimensions[1] * scale))
clock = pg.time.Clock()

board = np.zeros(dimensions) # walls
fire_map = np.zeros(dimensions)

for i in range(dimensions[0]):
    for j in range(dimensions[1]):
        if i % 2 == 0 and j % 2 == 0:
            board[i][j] = 1
class Fire:
    def __init__(self, instigator, position):
        self.size = 3
        self.life = 5
        self.x, self.y = position

    def tick(self):
        self.life -= 1
        if self.life == 0:
            fire_destruction_buffer.append(self)


class Bomb:
    def __init__(self, instigator):
        self.instigator = instigator
        self.fuse = 30
        self.x, self.y = (instigator.x, instigator.y)

    def tick(self):
        self.fuse -= 1
        if self.fuse == 0:
            self.instigator.ammo += 1
            destruction_buffer.append(self)
            fires.append(Fire(self, (self.x, self.y)))

class Bombot:
    NOP, UP, DOWN, LEFT, RIGHT, BOMB = range(6)

    def __init__(self, spawn_location):
        self.x, self.y = spawn_location # (i, j) = (x, y), [x][y]
        self.ammo = 1

    def act(self, action):
        # Movement
        if action == Bombot.UP:
            if self.y - 1 in range(dimensions[1]) and board[self.x][self.y - 1] == 0:
                self.y -= 1
        if action == Bombot.DOWN:
            if self.y + 1 in range(dimensions[1]) and board[self.x][self.y + 1] == 0:
                self.y += 1
        if action == Bombot.LEFT:
            if self.x - 1 in range(dimensions[0]) and board[self.x - 1][self.y] == 0:
                self.x -= 1
        if action == Bombot.RIGHT:
            if self.x + 1 in range(dimensions[0]) and board[self.x + 1][self.y] == 0:
                self.x += 1
        # Bombing
        if action == Bombot.BOMB:
            if self.ammo > 0:
                self.ammo -= 1
                bombs.append(Bomb(self))

bots = [Bombot((1, 0)), Bombot((3, 0))]
bombs = []
fires = []
destruction_buffer = []
fire_destruction_buffer = []
"""
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
            
    # clear image
    pg.draw.rect(screen, (24, 24, 24), (0, 0, dimensions[0] * scale, dimensions[1] * scale)) # x, y, w, h
    
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            if board[i][j] == 1:
                pg.draw.rect(screen, (64, 64, 64), (scale * i, scale * j, scale, scale)) # x, y, w, h
    for bot in bots:
        bot.act(random.randint(0, 5))
        pg.draw.rect(screen, (128, 0, 0), (scale * bot.x, scale * bot.y, scale, scale)) # x, y, w, h
    
    for bomb in bombs:
        bomb.tick()
        pg.draw.rect(screen, (0, 128, 0), (scale * bomb.x, scale * bomb.y, scale, scale)) # x, y, w, h
            
    for bomb in destruction_buffer:
        bombs.remove(bomb)

    destruction_buffer.clear()

    for fire in fires: 
        fire.tick()
        orange = (255, 149, 0)
        pg.draw.rect(screen, orange, (scale * fire.x, scale * fire.y, scale, scale)) # x, y, w, h
        for i in range(1, fire.size + 1):
            pg.draw.rect(screen, orange, (scale * (fire.x + i), scale * fire.y, scale, scale)) # x, y, w, h
            pg.draw.rect(screen, orange, (scale * (fire.x - i), scale * fire.y, scale, scale)) # x, y, w, h
            pg.draw.rect(screen, orange, (scale * fire.x, scale * (fire.y + i), scale, scale)) # x, y, w, h
            pg.draw.rect(screen, orange, (scale * fire.x, scale * (fire.y - i), scale, scale)) # x, y, w, h
    
    for fire in fire_destruction_buffer:
        fires.remove(fire)

    fire_destruction_buffer.clear()

    pg.display.flip()
    clock.tick(int(framerate))
"""