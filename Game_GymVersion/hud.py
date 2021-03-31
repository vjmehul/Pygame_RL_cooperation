import pygame
import constant as c
from healthbar import  healthbar
from score import Score

class HUD(pygame.sprite.Sprite):
    def __init__(self, hp):
        super(HUD, self).__init__()
        self.image = pygame.image.load('hud.png').convert_alpha()
        self.image= pygame.transform.scale(self.image,(930,250))
        self.rect = self.image.get_rect()
        self.rect.y = c.DISPLAY_SIZE[1] - self.rect.height - 10
        self.rect.x = 10
        self.vel_x = 0
        self.vel_y = 0
        # create heathbar
        self.healthbar = healthbar(hp)
        self.healthbar.rect.x = 200
        self.healthbar.rect.y = c.DISPLAY_SIZE[1] - self.rect.height+200
        self.healthbar_group = pygame.sprite.Group()
        self.healthbar_group.add(self.healthbar)

        self.score = Score()
        self.score_group = pygame.sprite.Group()
        self.score_group.add(self.score)



    def update(self):
        self.healthbar_group.update()
        self.score_group.update()
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y