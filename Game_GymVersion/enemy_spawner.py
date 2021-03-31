from enemy import Enemy
import pygame
import random
import constant as c


class EnemySpawner:
    def __init__(self):
        self.enemy_group = pygame.sprite.Group()
        self.spawn_timer = random.randrange(100, 120)

    def update(self):
        self.enemy_group.update()
        for enemy in self.enemy_group:
            if enemy.rect.y >= 600:
                enemy.self_distruct()

            if enemy.rect.y >= c.DISPLAY_SIZE[1]:
                self.enemy_group.remove(enemy)

        if self.spawn_timer == 0:
            self.spawn_enemy()
            self.spawn_timer = random.randrange(100,120)
        else:
            self.spawn_timer -= 1

    def spawn_enemy(self):
        new_enemy = Enemy()
        self.enemy_group.add(new_enemy)

