import pygame
import Game.constant as C
from Game.players import Gameplayer1, Gameplayer2
from Game.background import backG
from Game.enemy_spawner import EnemySpawner
from Game.partical_spawner import partical_spawner

display = pygame.display.set_mode(C.DISPLAY_SIZE)
# fps=60
clock = pygame.time.Clock()
pygame.font.init()

# Object setup

bg = backG()
bg_group = pygame.sprite.Group()
bg_group.add(bg)




player1 = Gameplayer1()
player2 = Gameplayer2()


enemy_spawner = EnemySpawner()
partical_spawner = partical_spawner()

sprit_group = pygame.sprite.Group()
sprit_group.add(player1)
sprit_group.add(player2)

angle_update1=0
angle_update2=0

bullet_count_red = 100
bullet_count_blue = 100
running = True
cool_down = 10000

while running:
    clock.tick(60)


    # pygame.event.pump()
    display.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    key_pressed = pygame.key.get_pressed()
    if key_pressed[pygame.K_RIGHT]:
        if not player1.angle <-65:
            player1.angle -= 2

    if key_pressed[pygame.K_LEFT]:
        if not player1.angle >65:
            player1.angle += 2

    if key_pressed[pygame.K_d]:
        if not player2.angle <-65:
            player2.angle -= 2

    if key_pressed[pygame.K_a]:
        if not player2.angle >65:
            player2.angle += 2

    if key_pressed[pygame.K_RCTRL]:
        print(bullet_count_red)
        if bullet_count_red >= 0:
            player1.shoot(player1.angle,display)
            bullet_count_red -= 1
        if bullet_count_red == 0:
            last = pygame.time.get_ticks()



    if key_pressed[pygame.K_SPACE]:
        print(bullet_count_blue)
        if bullet_count_blue >= 0:
            player2.shoot(player1.angle, display)
            bullet_count_blue -= 1
        if bullet_count_blue == 0:
            last_b = pygame.time.get_ticks()

    


# Collision detection
    collided_1 = pygame.sprite.groupcollide(player1.bullets_P1, enemy_spawner.enemy_group, True, False)
    collided_2 = pygame.sprite.groupcollide(player2.bullets_P2,enemy_spawner.enemy_group,True, False)

    for bullet, enemy in collided_1.items():
        enemy[0].get_hit()
        if not enemy[0].is_invincible:
            partical_spawner.spawn_particals((bullet.rect.x,bullet.rect.y))
            player1.hud.score.update_score(enemy[0].score_value)

    for bullet, enemy in collided_2.items():
        enemy[0].get_hit()
        if not enemy[0].is_invincible:
            partical_spawner.spawn_particals((bullet.rect.x,bullet.rect.y))
            player1.hud.score.update_score(enemy[0].score_value)

    for enemy in enemy_spawner.enemy_group:
        if enemy.rect.y == 600:
            player1.get_hit()
            player2.get_hit()
            player1.hud.score.update_score_reverse(enemy.penalty_value)
            break


    if player1.health == 0 or player2.health == 0:
        running = False
    # print(player1.health)

    # updates all the objects
    bg_group.update(display)
    bg_group.draw(display)
    sprit_group.update(display)
    enemy_spawner.update()
    partical_spawner.update()


    player1.bullets_P1.draw(display)
    player2.bullets_P2.draw(display)
    enemy_spawner.enemy_group.draw(display)
    partical_spawner.partical_group.draw(display)
    player1.hud.healthbar_group.draw(display)
    player1.hud_group.draw(display)
    player1.hud.score_group.draw(display)

    if bullet_count_red <= 0:
            now = pygame.time.get_ticks()
            diff = ((now - last)/1000)
            diff=round(diff)
            font = pygame.font.Font(None, 100)
            image_cooldown = font.render(str(diff), True, (16,52,166))
            image_cooldown = pygame.transform.scale(image_cooldown, (55,55))
            rect = image_cooldown.get_rect()
            rect.x = 642
            rect.y = 570
            display.blit(image_cooldown, (rect.x,rect.y))
            # print(diff)
            if now - last > cool_down:
                bullet_count_red = 100


    if bullet_count_blue <= 0:
        now_b = pygame.time.get_ticks()
        diff_b = ((now_b - last_b)/1000)
        diff_b=round(diff_b)
        font_b = pygame.font.Font(None, 100)
        image_cooldown_b = font_b.render(str(diff_b), True, (255,0,0))
        image_cooldown_b = pygame.transform.scale(image_cooldown_b, (55,55))
        rect_b = image_cooldown_b.get_rect()
        rect_b.x = 255
        rect_b.y = 570
        display.blit(image_cooldown_b, (rect_b.x,rect_b.y))
        # print(diff_b)
        if now_b - last_b > cool_down:
            bullet_count_blue = 100

    # print(player1.hud.score.show_score())
    pygame.display.update()
