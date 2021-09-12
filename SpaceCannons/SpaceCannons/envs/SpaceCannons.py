import re
from numpy.core.numeric import False_
from numpy.lib.type_check import imag
import pygame
import SpaceCannons.envs.Game.constant as C
from SpaceCannons.envs.Game.players import Gameplayer1, Gameplayer2
from SpaceCannons.envs.Game.background import backG
from SpaceCannons.envs.Game.enemy_spawner import EnemySpawner
from SpaceCannons.envs.Game.partical_spawner import partical_spawner
import numpy as np
from pygame import display, time, init
from pygame.surfarray import array3d
from pygame.event import pump
import pandas as pd
from gym.utils import seeding
# import cv2
from pygame.locals import *
import os

import gym
from gym import spaces



class SpaceCannons(gym.Env):
    def __init__(self):
        super(SpaceCannons, self).__init__()
        # os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        pygame.display.init()
        pygame.display.set_caption('DO NOT CLOSE THIS WINDOW--->Experiment in progress by mverma"')
        self.clock = pygame.time.Clock()
        self.history = []

        self.screen = display.set_mode(C.DISPLAY_SIZE)
        self.screen.fill((0, 0, 0))

        self.FRAME_COUNT=0
        self.action_space = [spaces.Discrete(4),spaces.Discrete(4)]
        self.observation_space = spaces.Box(low=0, high=255, shape=(950,700, 1), dtype=np.uint8)
        self.enemycount=0

        self.difficulty = C.game_difficulty_metric
        E2_per = int(str(self.difficulty) + "0")
        self.difficulty_weights = [100-E2_per, E2_per,0]
        print('initial setup complete')

    def reset(self):
        self.total_bullet_penalty=0
        self.screen.fill((0, 0, 0))

        self.bg = backG()
        self.bg_group = pygame.sprite.Group()
        self.bg_group.add(self.bg)
        
        self.game_level=2

        self.coop_hit_mini=0
        self.coop_hit_miniboss=0
        
        self.enemy1_kill_count=0
        self.enemy2_kill_count=0

        self.A1_kills =0
        self.A2_kills =0
        self.enemy1_evasive_count=0
        self.enemy2_evasive_count=0

        self.player1 = Gameplayer1()
        self.player2 = Gameplayer2()

        self.enemy_spawner = EnemySpawner()
        self.partical_spawner = partical_spawner()

        self.sprit_group = pygame.sprite.Group()
        self.sprit_group.add(self.player2)
        self.sprit_group.add(self.player1)

        # self.angle_update1=0
        # self.angle_update2=0

        self.bullet_count_red = 100000
        self.bullet_count_blue = 100000
        self.running = True
        self.cool_down = 100
        image = array3d(display.get_surface())
        return image

    def step(self, action):
        kill_stat=pd.DataFrame()
        self.FRAME_COUNT+=1
        

        # print(action)

        self.last_shot1=0
        self.last_shot2=0
        pump()
        done = False

        reward_1 = 0
        reward_2 = 0
        reward_3 = 0
        bullet_penalty_1 = 0
        bullet_penalty_2 = 0

        if action[0]==0:
            if not self.player1.angle <-70:
                self.player1.angle -= 6

        if action[0] == 1:
            if not self.player1.angle >70:
                self.player1.angle += 6

        if action[1] == 0:
            if not self.player2.angle <-70:
                self.player2.angle -= 6

        if action[1] == 1:
            if not self.player2.angle >70:
                self.player2.angle += 6

        # if fire_1:
        if action[0] == 2:

            if self.bullet_count_red >= 0:
                self.player1.shoot(self.player1.angle,self.screen)
                # bullet_penalty_1 -= 0.1
                # self.player1.hud.score.update_score(bullet_penalty_1)
                # self.bullet_count_red -= 1
            if self.bullet_count_red == 0:
                self.last = pygame.time.get_ticks()

        # if fire_2:
        if action[1] == 2:

            if self.bullet_count_blue >= 0:
                self.player2.shoot(self.player1.angle, self.screen)
                # self.bullet_count_blue -= 1
                # bullet_penalty_2 -= 0.1
                # self.player1.hud.score.update_score(bullet_penalty_2)
            if self.bullet_count_blue == 0:
                self.last_b = pygame.time.get_ticks()


# Collision detection
        collided_1 = pygame.sprite.groupcollide(self.player1.bullets_P1, self.enemy_spawner.enemy_group, False, False,pygame.sprite.collide_mask)
        collided_2 = pygame.sprite.groupcollide(self.player2.bullets_P2, self.enemy_spawner.enemy_group,False, False,pygame.sprite.collide_mask)



        if collided_1 and collided_2:
            if list(collided_1.values())[0][0].Enemy_id == list(collided_2.values())[0][0].Enemy_id and list(collided_2.values())[0][0].type=='mini':
                for bullet1, enemy1 in collided_1.items():
                    for bullet2, enemy2 in collided_2.items():
                        if enemy1[0].Enemy_id == enemy2[0].Enemy_id and enemy1[0].type=='mini' and not enemy1[0].hp <= 0:

                            enemy1[0].coordinate_hitcounts+=1
                            enemy1[0].single_hit_1+=1
                            enemy1[0].single_hit_2+=1
                            # if enemy1[0].hp<=2:
                            #     print('wtf')
                            #Game statistics
                            self.coop_hit_mini +=1

                            #kill enemy if the health is low
                            if enemy1[0].hp<=2 and enemy1[0].type=='mini':
                                self.enemy1_kill_count+=1
                            if enemy1[0].hp<=2 and enemy1[0].type=='miniboss':
                                self.enemy2_kill_count+=1

                            #decrease enemy health
                            enemy1[0].get_hit()
                            reward_1, reward_2, interdf = enemy2[0].get_hit()
                            if not interdf.empty:
                                kill_stat=kill_stat.append(interdf)
                            #destroy bullets
                            bullet2.kill()
                            del bullet2
                            #update scores on HUD
                            # self.player1.hud.score.update_score(1)
                            bullet1.kill()
                            del bullet1
                            break
                    break

            if list(collided_1.values())[0][0].Enemy_id == list(collided_2.values())[0][0].Enemy_id and list(collided_2.values())[0][0].type=='miniboss':
                for bullet1, enemy1 in collided_1.items():
                    for bullet2, enemy2 in collided_2.items():
                        if enemy1[0].Enemy_id == enemy2[0].Enemy_id and enemy1[0].type=='miniboss'  and not enemy1[0].hp <= 0:
                            enemy1[0].coordinate_hitcounts+=1

                            enemy1[0].single_hit_1+=1
                            enemy1[0].single_hit_2+=1

                            ###testing##
                            if enemy1[0].hp<=2:
                                print('wtf')

                            #Game statistics
                            self.coop_hit_miniboss +=1
                            if enemy1[0].hp<=1 and enemy1[0].type=='mini':
                                self.enemy1_kill_count+=1
                            if enemy1[0].hp<=1 and enemy1[0].type=='miniboss':
                                self.enemy2_kill_count+=1


                            #decrease enemy health
                            enemy1[0].get_hit()
                            reward_1, reward_2, interdf = enemy2[0].get_hit()
                            if not interdf.empty:
                               kill_stat=kill_stat.append(interdf)
                            #destroy bullets
                            bullet2.kill()
                            del bullet2
                            bullet1.kill()
                            del bullet1
                            break
                    break

        if collided_1:
            for bullet1, enemy1 in collided_1.items():
                # # creating statistics for the killed  enemy
                if  not enemy1[0].hp <= 0:
                    if enemy1[0].hp<=1 and enemy1[0].type=='mini':
                        self.enemy1_kill_count+=1
                        self.A1_kills +=1
                    if enemy1[0].hp<=1 and enemy1[0].type=='miniboss':
                        self.enemy2_kill_count+=1
                        self.A1_kills +=1
                    enemy1[0].single_hit_1 +=1
                    #hit the enemy
                    reward_1, reward_2,interdf = enemy1[0].get_hit()
                    if not interdf.empty:
                            kill_stat=kill_stat.append(interdf)

                    #destroy bullets
                    bullet1.kill()
                    del bullet1


        if collided_2:
            for bullet2, enemy2 in collided_2.items():

                if  not enemy2[0].hp <= 0:

                    # creating statistics for the killed  enemy
                    if enemy2[0].hp<=1 and enemy2[0].type=='mini':
                        self.enemy1_kill_count+=1
                        self.A2_kills +=1
                    if enemy2[0].hp<=1 and enemy2[0].type=='miniboss':
                        self.enemy2_kill_count+=1
                        self.A2_kills +=1

                    enemy2[0].single_hit_2 +=1

                    #hit the enemy
                    reward_1, reward_2,interdf = enemy2[0].get_hit()
                    if not interdf.empty:
                       kill_stat= kill_stat.append(interdf)
                    #destroy bullets
                    bullet2.kill()
                    del bullet2



        for enemy in self.enemy_spawner.enemy_group:
            if enemy.rect.y > 585:
                self.player1.get_hit()
                reward_3 = -1
                if enemy.type=='mini':
                    self.enemy1_evasive_count+=1
                if enemy.type=='miniboss':
                    self.enemy2_evasive_count+=1

                enemy.kill()


        if self.player1.health <= 0 or self.player2.health <= 0:
            running = False
            done = True

        for bullet in self.player1.bullets_P1:
            if  bullet.center[1] <= 7 or bullet.center[0] <=4 or bullet.center[0]>=950:
                bullet_penalty_1 += C.bullet_penalty
                self.total_bullet_penalty += C.bullet_penalty
                bullet.kill()

        for bullet in self.player2.bullets_P2:
            if  bullet.center[1] <= 7 or bullet.center[0] <=4 or bullet.center[0]>=950:
                bullet_penalty_2 += C.bullet_penalty
                self.total_bullet_penalty += C.bullet_penalty
                bullet.kill()

        agent1_reward = reward_1 + reward_3 - bullet_penalty_1
        agent2_reward = reward_2 + reward_3 - bullet_penalty_2

        global_reward = [agent1_reward,agent2_reward]
        # print(global_reward)

        self.player1.hud.score.update_score(agent1_reward+agent2_reward)


        image = array3d(display.get_surface())

        info={'Enemy1_kill':self.enemy1_kill_count,
              'Enemy2_kill':self.enemy2_kill_count,
              'enemy1_evasive_count':self.enemy1_evasive_count,
              'enemy2_evasive_count':self.enemy2_evasive_count,
              'coophit_mini':self.coop_hit_mini,
              'coophit_miniboss':self.coop_hit_miniboss,
              "A1_kills":self.A1_kills,
              "A2_kills":self.A2_kills,
                'Tot_Bullet_penalty':self.total_bullet_penalty}
        
        if not kill_stat.empty:
            kill_stat_dict=kill_stat.to_dict()
            info['kill_stat']=kill_stat_dict
        else:
            info['kill_stat']=pd.DataFrame()
        # increasing game level according to performance
        # if self.enemy1_kill_count>=150:
        #     self.game_level=2

        # if self.enemy2_kill_count>=50:
        #     self.game_level=3

        self.render(self.difficulty_weights)


        return image, global_reward, done, info


    def render(self,difficulty_weights):
        clock = pygame.time.Clock()

         # updates all the objects
        self.bg_group.update(self.screen)
        self.bg_group.draw(self.screen)
        self.sprit_group.update(self.screen)
        self.enemy_spawner.update(difficulty_weights)
        self.partical_spawner.update()


        self.enemy_spawner.enemy_group.draw(self.screen)
        self.partical_spawner.partical_group.draw(self.screen)
        self.player1.hud.healthbar_group.draw(self.screen)
        self.player1.hud_group.draw(self.screen)
        self.player1.hud.score_group.draw(self.screen)

        pygame.display.update()
        clock.tick(30)

    def get_screen(self):
        return array3d(display.get_surface())