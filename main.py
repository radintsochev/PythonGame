import pygame
from os.path import join
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player_ship.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 400
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_time = 600

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_time:
                self.can_shoot = True


    def update(self, keys, deltatime):
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * deltatime

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(all_sprites, laser_surface, self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surface, position):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom = position)
        self.direction = pygame.Vector2(0, -1)
        self.speed = 500

    def update(self, keys, deltatime):
        self.rect.center += self.direction * self.speed * deltatime
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        position = (random.randint(0, SCREEN_WIDTH), 0)
        self.rect = self.image.get_frect(center = position)
        self.direction = pygame.Vector2(0, 1)
        self.speed = 250

    def update(self, keys, deltatime):
        self.rect.center += self.direction * self.speed * deltatime
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        position = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.rect = self.image.get_frect(center = position)

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Battle")

all_sprites = pygame.sprite.Group()
laser_surface = pygame.image.load(join('images', 'laser.png')).convert_alpha()
enemy_surface = pygame.image.load(join('images', 'enemy_ship.png')).convert_alpha()
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()

for i in range(30):
    Star(all_sprites, star_surface)
player = Player(all_sprites)

running = True
clock = pygame.time.Clock()

enemy_event = pygame.event.custom_type()
pygame.time.set_timer(enemy_event, 1000)

while running:
    deltatime = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == enemy_event:
            Enemy(all_sprites, enemy_surface)

    #input
    keys = pygame.key.get_pressed()
    all_sprites.update(keys, deltatime)

    #draw the game
    screen.fill('#0a205a')
    all_sprites.draw(screen)
    pygame.display.update()
pygame.quit()
