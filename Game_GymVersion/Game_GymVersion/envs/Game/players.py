import pygame
import Game.constant as C
from Game.bullet import bullet1
from Game.bullet import bullet2
from Game.hud import HUD

class Gameplayer1(pygame.sprite.Sprite):

    def __init__(self):
        super(Gameplayer1, self).__init__()
        self.image = pygame.image.load(r'C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/player1.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 1100))
        self.rect = self.image.get_rect()
        self.rect.x = C.P1_pos_x
        self.rect.y = C.P1_pos_y
        self.angle = 0


        # Bullet
        self.bullets_P1 = pygame.sprite.Group()
        self.max_hp = 50
        self.health = self.max_hp
        ##  HUD
        self.hud = HUD(self.health)
        self.hud_group = pygame.sprite.Group()
        self.hud_group.add(self.hud)



    def update(self,display):
        self.bullets_P1.update(self.angle)

        #hud UPDATE
        self.hud_group.update()

        # fix memory leave of bullets
        for bullets in self.bullets_P1:
            if bullets.rect.y <= 0:
                self.bullets_P1.remove(bullet1)


        # print(self.rect.x,self.rect.y)
        imagex = pygame.transform.rotozoom(self.image, self.angle,1)

        self.rect = imagex.get_rect(center=self.rect.center)

        display.blit(imagex, self.rect)


    def shoot(self,angle,display):
        new_bullet = bullet1(self.rect.center, self.angle)
        new_bullet.rect.x = self.rect.x + (self.rect.width //2 -1)
        new_bullet.rect.y = self.rect.y

        self.bullets_P1.add(new_bullet)

    def get_hit(self):
        self.health -=1
        self.hud.healthbar.decrease_hp()


class Gameplayer2(pygame.sprite.Sprite):

    def __init__(self):
        super(Gameplayer2, self).__init__()
        self.image = pygame.image.load(r'C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/player2.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60,1100))
        self.rect = self.image.get_rect()
        self.rect.x = C.P2_pos_x
        self.rect.y = C.P2_pos_y
        self.angle = 0
        self.health = 100

         #bullet
        self.bullets_P2 = pygame.sprite.Group()

    def update(self,display):
        self.bullets_P2.update(self.angle)
        for bullets in self.bullets_P2:
            if bullets.rect.y <= 0:
                self.bullets_P2.remove(bullet2)



        imagex = pygame.transform.rotozoom(self.image, self.angle,1)

        self.rect = imagex.get_rect(center=self.rect.center)

        display.blit(imagex, self.rect)

    def shoot(self,angle,display):
        new_bullet = bullet2(self.rect.center, self.angle)
        new_bullet.rect.x = self.rect.x + (self.rect.width //2 -1)
        new_bullet.rect.y = self.rect.y

        self.bullets_P2.add(new_bullet)

    def get_hit(self):
        self.health -= 1
