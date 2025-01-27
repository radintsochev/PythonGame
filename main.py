import pygame
from os.path import join
import random

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Battle")

running = True
clock = pygame.time.Clock()

surface = pygame.Surface((80, 80))
surface.fill('purple')
x = 0

player_surface = pygame.image.load(join('images', 'player_ship.png')).convert_alpha()
player_rectangle = player_surface.get_frect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
player_direction = pygame.Vector2()
player_speed = 300

star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()

star_positions = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for i in range(30)]

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
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
        #     print(1)
        # if event.type == pygame.MOUSEMOTION:
        #     player_rectangle.center = event.pos

    #input
    keys = pygame.key.get_pressed()
    
    #print(pygame.mouse.get_rel())
    player_direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    player_direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
    player_direction = player_direction.normalize() if player_direction else player_direction
    player_rectangle.center += player_direction * player_speed * deltatime

    recent_keys = pygame.key.get_just_pressed()
    if recent_keys[pygame.K_SPACE]:
        print('fire laser')
    
    #draw the game
    screen.fill('cadetblue4')
    for position in star_positions:
        screen.blit(star_surface, position)
    
    screen.blit(laser_surface, laser_rectangle)
    screen.blit(enemy_surface, enemy_rectangle)
    screen.blit(player_surface, player_rectangle)

    pygame.display.update()
pygame.quit()
