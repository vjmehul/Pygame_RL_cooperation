import pygame
import constant as c

class Score(pygame.sprite.Sprite):
    def __init__(self):
        super(Score, self).__init__()

        self.value = 0
        self.font_size = 50
        self.font = pygame.font.Font(None, self.font_size)
        self.color=(16,52,166)
        self.image = self.font.render(str(self.value),True ,self.color)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image,(50,45))
        self.rect.x = c.DISPLAY_SIZE[1] - self.rect.width - 590
        self.rect.y = c.DISPLAY_SIZE[1] - self.rect.width - 40

    def update(self):
        pass


    def update_score(self,value):
        self.value +=  value
        self.image = self.font.render(str(self.value), True, self.color)
        self.image = pygame.transform.scale(self.image, (80, 70))
        self.rect = self.image.get_rect()
        self.rect.x = c.DISPLAY_SIZE[1] - self.rect.width - 550
        self.rect.y = c.DISPLAY_SIZE[1] - self.rect.width +10

    def update_score_reverse(self,value):
        self.value -= value
        self.image = self.font.render(str(self.value), True, self.color)
        self.image = pygame.transform.scale(self.image, (80, 70))
        self.rect = self.image.get_rect()
        self.rect.x = c.DISPLAY_SIZE[1] - self.rect.width - 550
        self.rect.y = c.DISPLAY_SIZE[1] - self.rect.width + 10
