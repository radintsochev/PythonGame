import random
import pygame
from typing import List, Tuple
from config import PATHS, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_SETTINGS

class Player(pygame.sprite.Sprite):
    '''
    This class represents the player ship.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], laser_groups: List[pygame.sprite.Group], laser_sound: pygame.mixer.Sound) -> None:
        super().__init__(groups)
        self.image = pygame.image.load(PATHS['player']).convert_alpha()
        self.rect = self.image.get_frect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 400
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_time = 600
        self.laser_groups = laser_groups
        self.laser_sound = laser_sound

    def laser_timer(self) -> None:
        '''
        Enables the cooldown for shooting.
        '''
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_time:
                self.can_shoot = True

    def update(self, keys: pygame.key.ScancodeWrapper, deltatime: float) -> None:
        '''
        Moves the player, getting the input from the keyboard.
        '''
        can_left = self.rect.left > 0
        can_right = self.rect.right < SCREEN_WIDTH
        can_up = self.rect.top > 0
        can_down = self.rect.bottom < SCREEN_HEIGHT

        self.direction.x = keys[pygame.K_RIGHT] * can_right - keys[pygame.K_LEFT] * can_left
        self.direction.y = keys[pygame.K_DOWN] * can_down - keys[pygame.K_UP] * can_up

        if self.direction:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * self.speed * deltatime

        if keys[pygame.K_SPACE] and self.can_shoot:
            Laser(self.laser_groups, pygame.image.load(PATHS['laser']), self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            self.laser_sound.play()

        self.laser_timer()

class Laser(pygame.sprite.Sprite):
    '''
    This class represents the laser shot from the player.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], surface: pygame.Surface, position: Tuple[int, int]) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom=position)
        self.speed = 500

    def update(self, _: None, deltatime: float) -> None:
        '''
        Moves the laser foward.
        '''
        self.rect.y -= self.speed * deltatime
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    '''
    This class represents the enemy ships.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], surface: pygame.Surface) -> None:
        super().__init__(groups)
        self.image = surface
        enemy_width = self.image.get_size()[0]
        position = (random.randint(enemy_width//2, SCREEN_WIDTH - enemy_width//2), 0)
        self.rect = self.image.get_frect(center=position)
        self.speed = 250

    def update(self, _: None, deltatime: float) -> None:
        '''
        Moves the enemy down towards the player.
        '''
        self.rect.y += self.speed * deltatime
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    '''
    This class represents the explosion after destoying the enemies.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], frames: List[pygame.Surface], position: Tuple[int, int]) -> None:
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=position)

    def update(self, _: None, deltatime: float) -> None:
        '''
        Animates the explosion.
        '''
        self.frame_index += 25 * deltatime
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class UpgradeIcon(pygame.sprite.Sprite):
    '''
    This class represents the upgrades that someties spawn after killing an enemy.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], surface: pygame.Surface, position: Tuple[int, int]) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center=position)
        self.lifetime = 0

    def update(self, _: None, deltatime: float) -> None:
        '''
        Checks if it's time to despawn the icon.
        '''
        self.lifetime += 1000 * deltatime
        if self.lifetime >= GAME_SETTINGS['upgrade_lifetime']:
            self.kill()

class Star(pygame.sprite.Sprite):
    '''
    This class represents the stars in the background.
    '''
    def __init__(self, groups: List[pygame.sprite.Group], surface: pygame.Surface, rect: pygame.Rect) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = rect
