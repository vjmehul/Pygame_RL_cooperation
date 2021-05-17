from os import startfile
from numpy.lib.type_check import imag
import pygame
import Game.constant as C
from Game.players import Gameplayer1, Gameplayer2
from Game.background import backG
from Game.enemy_spawner import EnemySpawner
from Game.partical_spawner import partical_spawner
import numpy as np
from pygame import display, time, init
from pygame.surfarray import array3d
from pygame.event import pump
from gym.utils import seeding
import cv2
from pygame.locals import *



import gym
from gym import spaces



class custom_game_env(gym.Env):
    def __init__(self):
        super(custom_game_env, self).__init__()
        pygame.init()

        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.history = []
        for i in range(0, 6):
            self.history.append(np.zeros((84, 84)))

        self.screen = display.set_mode(C.DISPLAY_SIZE)
        self.screen.fill((0, 0, 0))
        # n_actions = 3
        
        # self.action_space = spaces.MultiDiscrete([ 2, 2, 2, 2, 2, 2 ])
        # self.observation_space = spaces.Box(low=0, high=255, shape=(252, 84, 3), dtype=np.uint8)

        self.action_space = spaces.Discrete(8)
        self.observation_space = spaces.Box(low=0, high=255, shape=(252, 84, 1), dtype=np.uint8)


    def reset(self):
        self.history_fame_11= np.zeros((84, 84))
        self.history_fame_12= np.zeros((84, 84))

        self.history_fame_21= np.zeros((84, 84))
        self.history_fame_22= np.zeros((84, 84))
        self.screen.fill((0, 0, 0))

        self.bg = backG()
        self.bg_group = pygame.sprite.Group()
        self.bg_group.add(self.bg)

        self.bullet_penalty = 0
        self.player1 = Gameplayer1()
        self.player2 = Gameplayer2()

        self.enemy_spawner = EnemySpawner()
        self.partical_spawner = partical_spawner()

        self.sprit_group = pygame.sprite.Group()
        self.sprit_group.add(self.player1)
        self.sprit_group.add(self.player2)

        self.angle_update1=0
        self.angle_update2=0

        self.bullet_count_red = 100
        self.bullet_count_blue = 100
        self.running = True
        self.cool_down = 10000
        image = self.pre_processing(array3d(display.get_surface()))

        return image

    def step(self, action):
        # print(action)
        self.screen.fill((0, 0, 0))

        pump()

        done = False

        reward_1 = 0
        reward_2 = 0
        penalty = 0
        
        # print(action)
        # left_1 = action[0]
        # right_1= action[1]
        # fire_1 = action[2]

        # left_2 = action[3]
        # right_2 = action[4]
        # fire_2 = action[5]
       # [0,1,2,3,4,5,6,7]
       # ['player1_left' : 0 ,'player1_right': 1,'player1_fire' : 2,'player1_noop' : 3,'player2_left' : 4 ,'player2_right' : 5 ,'player2_fire' : 6 ,'player1_noop': 7]

        # if left_1:
        if action==0:
            if not self.player1.angle <-65:
                self.player1.angle -= 2

        # if right_1:
        if action == 1:
            if not self.player1.angle >65:
                self.player1.angle += 2

        # if left_2:
        if action == 3:
            if not self.player2.angle <-65:
                self.player2.angle -= 2

        # if right_2:
        if action == 5:
            if not self.player2.angle >65:
                self.player2.angle += 2

        # if fire_1:
        if action == 2:
            penalty-=1
            if self.bullet_count_red >= 0:
                self.player1.shoot(self.player1.angle,display)
                self.player1.hud.score.update_score_reverse(self.bullet_penalty)
                self.bullet_count_red -= 1
            if self.bullet_count_red == 0:
                self.last = pygame.time.get_ticks()

        # if fire_2:
        if action == 6:
            # print(self.bullet_count_blue)
            penalty -= 0.01
            if self.bullet_count_blue >= 0:
                self.player2.shoot(self.player1.angle, display)
                self.bullet_count_blue -= 1
                self.player1.hud.score.update_score_reverse(self.bullet_penalty)
            if self.bullet_count_blue == 0:
                self.last_b = pygame.time.get_ticks()


# Collision detection
        collided_1 = pygame.sprite.groupcollide(self.player1.bullets_P1, self.enemy_spawner.enemy_group, False, False)
        collided_2 = pygame.sprite.groupcollide(self.player2.bullets_P2, self.enemy_spawner.enemy_group,False, False)

        for bullet1, enemy1 in collided_1.items():

            self.player1.hud.score.update_score(enemy1[0].score_value)
            enemy1[0].get_hit()
            bullet1.kill()
            reward_1 += enemy1[0].score_value
            if not enemy1[0].is_invincible:
                self.partical_spawner.spawn_particals((bullet1.rect.x,bullet1.rect.y))


        for bullet2, enemy2 in collided_2.items():
            self.player1.hud.score.update_score(enemy2[0].score_value)
            enemy2[0].get_hit()
            reward_2 += enemy2[0].score_value
            bullet2.kill()
            if not enemy2[0].is_invincible:
                self.partical_spawner.spawn_particals((bullet2.rect.x,bullet2.rect.y))


        for enemy in self.enemy_spawner.enemy_group:
            if enemy.rect.y == 600:
                self.player1.get_hit()
                # self.player2.get_hit()
                enemy.kill()
                self.player1.hud.score.update_score_reverse(enemy.penalty_value)

        if self.player1.health <= 0 or self.player2.health <= 0:
            running = False
            done = True

        global_reward_1 = self.player1.hud.score.show_score()
        self.render()
        image = self.pre_processing(array3d(display.get_surface()))
        info = {'score_1': reward_1, 'Score_2:': reward_2}
        # print(penalty)
        # cv2.imshow('', image)
        # cv2.waitKey(1)
        # return self.pre_processing(image), global_reward_1, reward_1, reward_2, penalty, done, info
        # print(global_reward_1)
        return image, global_reward_1, done, info


    def render(self):
         # updates all the objects
        self.bg_group.update(self.screen)
        self.bg_group.draw(self.screen)
        self.sprit_group.update(self.screen)
        self.enemy_spawner.update()
        self.partical_spawner.update()


        self.player1.bullets_P1.draw(self.screen)
        self.player2.bullets_P2.draw(self.screen)
        self.enemy_spawner.enemy_group.draw(self.screen)
        self.partical_spawner.partical_group.draw(self.screen)
        self.player1.hud.healthbar_group.draw(self.screen)
        self.player1.hud_group.draw(self.screen)
        self.player1.hud.score_group.draw(self.screen)
    
        if self.bullet_count_red <= 0:
               now = pygame.time.get_ticks()
               diff = ((now - self.last)/1000)
               diff=round(diff)
               font = pygame.font.Font(None, 100)
               image_cooldown = font.render(str(diff), True, (16,52,166))
               image_cooldown = pygame.transform.scale(image_cooldown, (55,55))
               rect = image_cooldown.get_rect()
               rect.x = 670
               rect.y = 500
               image_cooldown2 = pygame.draw.arc(self.screen,  (255,0,0), (550, 413, 200, 200), 10, 20, 7)
               self.screen.blit(image_cooldown, (rect.x,rect.y))
            #    self.screen.blit(image_cooldown2, (rect.x,rect.y))
               # print(diff)
               if now - self.last > self.cool_down:
                   self.bullet_count_red = 100


        if self.bullet_count_blue <= 0:
            now_b = pygame.time.get_ticks()
            diff_b = ((now_b - self.last_b)/1000)
            diff_b=round(diff_b)
            font_b = pygame.font.Font(None, 100)
            image_cooldown_b = font_b.render(str(diff_b), True, (255,0,0))
            image_cooldown_b = pygame.transform.scale(image_cooldown_b, (55,55))
            rect_b = image_cooldown_b.get_rect()
            rect_b.x = 260
            rect_b.y = 500
            image_cooldown2 = pygame.draw.arc(self.screen,  (16,52,166), (190, 413, 200, 200), 10, 20, 7)
            self.screen.blit(image_cooldown_b, (rect_b.x,rect_b.y))
            # print(diff_b)
            if now_b - self.last_b > self.cool_down:
                self.bullet_count_blue = 100

        pygame.display.update()



    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def pre_processing(self, image):
        
        image=image[:, 0:610]
        image = cv2.cvtColor(cv2.resize(image, (84, 84)), cv2.COLOR_BGR2GRAY)
        # image = cv2.resize(image, (84, 84))
        _, image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
        image = image / 255
        del self.history[0]
        self.history.append(image)
        # print(type(image))
        # print(image.shape)
        image = np.concatenate((self.history[-5], self.history[-3], image), axis=0)
        image = np.expand_dims(image, axis=-1)    # without (252, 84, 1) #with (252, 84, 1, 1) #axis=0 (1, 252, 84, 1)

        # print(image.shape)
        cv2.imshow('', image)
        cv2.waitKey(1)


        return image

