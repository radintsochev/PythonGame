import pygame
from os.path import join
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player_ship.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 300

    def update(self, keys, deltatime):
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * deltatime

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            print('fire laser')

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

running = True
clock = pygame.time.Clock()

surface = pygame.Surface((80, 80))
surface.fill('purple')
x = 0

all_sprites = pygame.sprite.Group()
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()

for i in range(30):
    Star(all_sprites, star_surface)
player = Player(all_sprites)


enemy_surface = pygame.image.load(join('images', 'enemy_ship.png')).convert_alpha()
enemy_rectangle = enemy_surface.get_frect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

laser_surface = pygame.image.load(join('images', 'laser.png')).convert_alpha()
laser_rectangle = laser_surface.get_frect(bottomleft = (20, SCREEN_HEIGHT - 20))


while running:
    deltatime = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #input
    keys = pygame.key.get_pressed()
    all_sprites.update(keys, deltatime)

    #draw the game
    screen.fill('#0a205a')
    all_sprites.draw(screen)
    pygame.display.update()
pygame.quit()
