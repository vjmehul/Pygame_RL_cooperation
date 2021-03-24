import pygame
import math


class bullet1(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super(bullet1, self).__init__()

       #create bullet
        self.image = pygame.image.load('fire_sword_2.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 60))
        self.image = pygame.transform.rotate(self.image, angle)


       # define bullet positions
        self.rect = self.image.get_rect()
        self.vel_x = 0
        self.vel_y = -20
        self.angle = 0

        # Use trigonometry to calculate the velocity.
        self.velocity_x = math.cos(math.radians(-angle)) * self.vel_y
        self.velocity_y = -math.sin(math.radians(-angle)) * self.vel_y
        self.pos = list(pos)

    def update(self,angle):

        self.pos[1] += self.velocity_x
        self.pos[0] += self.velocity_y
        # Update the position of the rect as well.
        self.rect.center = self.pos

class bullet2(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super(bullet2, self).__init__()

       #create bullet
        self.image = pygame.image.load('blue_bullet.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (15,60))
        self.image = pygame.transform.rotate(self.image, angle)


       # define bullet positions
        self.rect = self.image.get_rect()
        self.vel_x = 0
        self.vel_y = -20
        self.angle = 0

        # Use trigonometry to calculate the velocity.
        self.velocity_x = math.cos(math.radians(-angle)) * self.vel_y
        self.velocity_y = -math.sin(math.radians(-angle)) * self.vel_y
        self.pos = list(pos)

    def update(self,angle):

        self.pos[1] += self.velocity_x
        self.pos[0] += self.velocity_y
        # Update the position of the rect as well.
        self.rect.center = self.pos