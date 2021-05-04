import pygame
import Game.constant as c
import random
from Game.players import Gameplayer1, Gameplayer2


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        weak_enemy_list = ['dragon1.png','dragon2.png','dragon3.png','dragon4.png']
        rannum = random.randrange(1,4)
        enemy_string='C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/'+weak_enemy_list[rannum]
        self.image = pygame.image.load(enemy_string).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80,80))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, c.DISPLAY_SIZE[0] - self.rect.width)
        self.rect.y = -self.rect.height
        self.vel_x = 0
        self.hp = 20
        self.vel_y = random.randrange(1,3)
        self.score_value = 5
        self.penalty_value = 100

        # Explosion Animation


        self.img_b_explosion_01 = pygame.image.load(r'C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion/blue-explosion-1.png').convert_alpha()
        self.img_b_explosion_01 = pygame.transform.scale(self.img_b_explosion_01, (100, 100))

        self.img_b_explosion_02 = pygame.image.load('C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion//blue-explosion-2.png').convert_alpha()
        self.img_b_explosion_02 = pygame.transform.scale(self.img_b_explosion_02, (100, 100))

        self.img_b_explosion_03 = pygame.image.load('C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion//blue-explosion-3.png').convert_alpha()
        self.img_b_explosion_03 = pygame.transform.scale(self.img_b_explosion_03, (100, 100))

        self.img_b_explosion_04 = pygame.image.load('C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion//blue-explosion-4.png').convert_alpha()
        self.img_b_explosion_04 = pygame.transform.scale(self.img_b_explosion_04, (100, 100))

        self.img_b_explosion_05 = pygame.image.load('C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion//blue-explosion-5.png').convert_alpha()
        self.img_b_explosion_05 = pygame.transform.scale(self.img_b_explosion_05, (100, 100))

        self.img_b_explosion_06 = pygame.image.load('C:/Users/Shizu/Desktop/Pygame_RL/Pygame_RL_cooperation/Game_GymVersion/Game_GymVersion/envs/Game_imgs/blue_explosion//blue-explosion-6.png').convert_alpha()
        self.img_b_explosion_06 = pygame.transform.scale(self.img_b_explosion_06, (100, 100))



        self.anim_explosion1 = [self.img_b_explosion_01,
                               self.img_b_explosion_02,
                               self.img_b_explosion_03,
                               self.img_b_explosion_04,
                               self.img_b_explosion_05,
                               self.img_b_explosion_06,
                              ]


        self.anime1_index = 0
        self.max_frame_length = 1
        self.frame_length = self.max_frame_length
        self.is_destroyed = False
        self.is_invincible = False

    def update(self):

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.is_destroyed:
            max_index = len(self.anim_explosion1) - 1
            if self.frame_length ==0:
                self.anime1_index +=1
                if self.anime1_index > max_index:
                    self.kill()
                else:
                    self.image = self.anim_explosion1[self.anime1_index]
                    self.frame_length = self.max_frame_length
            else:
                self.frame_length -= 1




    # red explosion
    def get_hit(self):
        if not self.is_invincible:
            self.hp -= 1
            if self.hp <= 0:
                self.is_invincible = True
                self.is_destroyed = True
                self.vel_x = 0
                self.vel_y = 0
                self.rect.x = self.rect.x - 32
                self.rect.y = self.rect.y - 32
                self.image = self.anim_explosion1[self.anime1_index]
        else:
            pass



    def self_distruct(self):

        self.is_destroyed = True






