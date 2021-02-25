import os
import pygame as pg



class TexMan: # Texture Manager
    def __init__(self, scale):
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, 'res','bb_sprites.png')
        self.spr = pg.image.load(filename).convert_alpha()
        self.src_scale = 32
        self.dst_scale = scale
        #sprite = pg.Surface((self.scale, self.scale), pg.SRCALPHA)
        #sprite.blit(self.spr, (0, 0, 32, 32), (32, 0, 32, 32)) # source, dest, source area
        #for i in range(8):
        #    self.screen.blit(sprite, (self.scale * i, 0, 32, 32))
        self.spr_floor = self.copy_spr((5, 0))
        self.spr_box = self.copy_spr((5, 1))
        self.spr_wall = self.copy_spr((6, 0))

        self.spr_bot1_n = self.copy_spr((0, 1))
        self.spr_bot1_s = self.copy_spr((0, 0))
        self.spr_bot1_e = self.copy_spr((0, 2))
        self.spr_bot1_w = self.copy_spr((0, 3))

        self.spr_bot2_n = self.copy_spr((2, 1))
        self.spr_bot2_s = self.copy_spr((2, 0))
        self.spr_bot2_e = self.copy_spr((2, 2))
        self.spr_bot2_w = self.copy_spr((2, 3))
        
        self.spr_bomb = self.copy_spr((4, 0))

        self.spr_fire_n = self.copy_spr((7, 0))
        self.spr_fire_s = self.copy_spr((7, 3))
        self.spr_fire_e = self.copy_spr((6, 3))
        self.spr_fire_w = self.copy_spr((6, 1))
        self.spr_fire_h = self.copy_spr((6, 2))
        self.spr_fire_v = self.copy_spr((7, 2))
        self.spr_fire_x = self.copy_spr((7, 1))


    def copy_spr(self, pos):
        spr = pg.Surface((self.src_scale, self.src_scale), pg.SRCALPHA)
        spr.blit(self.spr, (0, 0, self.src_scale, self.src_scale), (self.src_scale * pos[0], self.src_scale * pos[1], self.src_scale, self.src_scale))
        return pg.transform.scale(spr, (self.dst_scale, self.dst_scale))
        