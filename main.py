import pygame
from os.path import join
import random
import functools

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('game_assets', 'player_ship.png')).convert_alpha()
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
            Laser((all_sprites, laser_sprites), laser_surface, self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound_effect.play()

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

class Explosion(pygame.sprite.Sprite):
    def __init__(self, groups, frames, position):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center = position)
        explosion_sound_effect.play()

    def update(self, keys,  deltatime):
        self.frames_index += 25 * deltatime
        if self.frames_index < len(self.frames):            
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surface, rect):
        super().__init__(groups)
        self.image = surface
        self.rect = rect

def laser_collisions():
    for laser in laser_sprites:
        collided_enemies = pygame.sprite.spritecollide(laser, enemy_sprites, True, pygame.sprite.collide_mask)
        if collided_enemies:
            laser.kill()
            Explosion(all_sprites, explosion_frames, laser.rect.midtop)

def player_collisions():
    if pygame.sprite.spritecollide(player, enemy_sprites, True, pygame.sprite.collide_mask):
        damage_sound_effect.play()
        player.kill()
        game_over_screen()

def display_time_passsed():
    current_time = pygame.time.get_ticks() // 1000
    timer_title_surface = font.render('Time: ', True, (230, 230, 230))
    timer_title_rect = timer_title_surface.get_frect(topleft = (10, 20))
    timer_surface = font.render(str(current_time), True, (230, 230, 230))
    timer_rect = timer_surface.get_frect(topleft = timer_title_rect.topright)
    screen.blit(timer_title_surface, timer_title_rect)
    screen.blit(timer_surface, timer_rect)
    pygame.draw.rect(screen, (230, 230, 230), timer_rect.inflate(15, 15), 5, 5)

def fade(width, height): 
    fade = pygame.Surface((width, height))
    fade.fill((0,0,0))
    for alpha in range(0, 300):
        fade.set_alpha(alpha)
        screen.fill('#2c205a')
        all_sprites.draw(screen)
        display_time_passsed()
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)

def game_over_screen():
    global running
    fade(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_over = True
    game_over_text_surface = game_over_font.render('Game Over', True, (255, 0, 0))
    game_over_text_rect = game_over_text_surface.get_frect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    game_over_info_surface = font.render('Press any key to exit...', True, (255, 0, 0))
    game_over_info_rect = game_over_info_surface.get_frect(midtop = game_over_text_rect.inflate(15, 15).midbottom)
    screen.fill('black')
    screen.blit(game_over_text_surface, game_over_text_rect)
    screen.blit(game_over_info_surface, game_over_info_rect)
    pygame.display.flip()
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                game_over = False
    running = False

def generate_stars(num_stars):
    star_width, star_height = star_surface.get_size()
    star_positions = []
    max_tries = 50
    for _ in range(num_stars):
        tries_count = 0
        while True:
            if tries_count > max_tries:
                break
            x = random.randint(0, SCREEN_WIDTH - star_width)
            y = random.randint(0, SCREEN_HEIGHT - star_height)

            # Create a rect for the new star
            new_star_rect = pygame.Rect(x, y, star_width, star_height)

            # Check for overlap with existing stars
            
            if not any(new_star_rect.colliderect(existing) for existing in star_positions):
                star_positions.append(new_star_rect)
                break  # Exit loop when a valid position is found
            else:
                tries_count += 1

    return star_positions

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Battle")

all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
star_sprites = pygame.sprite.Group()

font = pygame.font.Font(join('game_assets', "Sterion-BLLld.ttf"), 30)
game_over_font = pygame.font.Font(join('game_assets', "Sterion-BLLld.ttf"), 100)

laser_surface = pygame.image.load(join('game_assets', 'laser.png')).convert_alpha()
enemy_surface = pygame.image.load(join('game_assets', 'enemy_ship.png')).convert_alpha()
star_surface = pygame.image.load(join('game_assets', 'star.png')).convert_alpha()
explosion_frames = [pygame.image.load(join('game_assets', 'explosion', f'{i}.png')).convert_alpha() for i in range(1, 13)]

laser_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'laser_sound.mp3'))
laser_sound_effect.set_volume(0.15)
explosion_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'explosion_sound.mp3'))
explosion_sound_effect.set_volume(0.25)
damage_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'damage_sound.mp3'))
background_music = pygame.mixer.Sound(join('game_assets', 'sounds', 'background_music.mp3'))
background_music.set_volume(0.1)
background_music.play(loops= -1)

star_rects = generate_stars(70)

for rect in star_rects:
    Star((all_sprites, star_sprites), star_surface, rect)
player = Player(all_sprites)

running = True
game_over = False
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
            Enemy((all_sprites, enemy_sprites), enemy_surface)

    #input
    keys = pygame.key.get_pressed()
    all_sprites.update(keys, deltatime)
    
    laser_collisions()
    player_collisions()

    #draw the game
    if running:
        screen.fill('#2c205a')
        all_sprites.draw(screen)
        display_time_passsed()
        pygame.display.update()
pygame.quit()
