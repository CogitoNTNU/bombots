import os
import pygame as pg

class TexMan: # Texture Manager
    def __init__(self, scale):
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, 'res','bb_sprites.png')
        self.spr = pg.image.load(filename).convert_alpha()
        
        self.src_scale = 32    # Determined by sheet
        self.dst_scale = scale # Determined by environment
        
        # [TODO: Make this into a dictionary, add animation system]
        self.spr_floor = self.copy_spr((5, 0))
        self.spr_box = self.copy_spr((5, 1))
        self.spr_wall = self.copy_spr((6, 0))

        self.spr_bot = {
            'red' : {
                'n' : self.copy_spr((0, 1)),
                's' : self.copy_spr((0, 0)),
                'e' : self.copy_spr((0, 2)),
                'w' : self.copy_spr((0, 3))
            },
            'green' : {
                'n' : self.copy_spr((1, 1)),
                's' : self.copy_spr((1, 0)),
                'e' : self.copy_spr((1, 2)),
                'w' : self.copy_spr((1, 3))
            },
            'blue' : {
                'n' : self.copy_spr((2, 1)),
                's' : self.copy_spr((2, 0)),
                'e' : self.copy_spr((2, 2)),
                'w' : self.copy_spr((2, 3))
            },
            'yellow' : {
                'n' : self.copy_spr((3, 1)),
                's' : self.copy_spr((3, 0)),
                'e' : self.copy_spr((3, 2)),
                'w' : self.copy_spr((3, 3))
            }
        }

        
        self.spr_pop_ext = self.copy_spr((5, 2))
        self.spr_pop_num = self.copy_spr((5, 3))

        self.spr_bomb = [
            self.copy_spr((4, 0)),
            self.copy_spr((4, 1)),
            self.copy_spr((4, 2)),
            self.copy_spr((4, 3))
        ]

        self.spr_fire = {
            'n' : self.copy_spr((7, 0)),
            's' : self.copy_spr((7, 3)),
            'e' : self.copy_spr((6, 3)),
            'w' : self.copy_spr((6, 1)),
            'h' : self.copy_spr((6, 2)),
            'v' : self.copy_spr((7, 2)),
            'x' : self.copy_spr((7, 1))
        }

        self.spr_fire_n = self.copy_spr((7, 0)) # North end
        self.spr_fire_s = self.copy_spr((7, 3)) # South end
        self.spr_fire_e = self.copy_spr((6, 3)) # East end
        self.spr_fire_w = self.copy_spr((6, 1)) # West end
        self.spr_fire_h = self.copy_spr((6, 2)) # Horizontal beam
        self.spr_fire_v = self.copy_spr((7, 2)) # Vertical beam
        self.spr_fire_x = self.copy_spr((7, 1)) # Cross-section

    def copy_spr(self, pos): # Copy specific sprite from sheet to surface (pos is sheet index, not in pixels)
        spr = pg.Surface((self.src_scale, self.src_scale), pg.SRCALPHA)
        spr.blit(self.spr, (0, 0, self.src_scale, self.src_scale), (self.src_scale * pos[0], self.src_scale * pos[1], self.src_scale, self.src_scale))
        return pg.transform.scale(spr, (self.dst_scale, self.dst_scale))