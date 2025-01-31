import pygame
from os.path import join
import random
import numpy as np

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
        can_up, can_down, can_right, can_left = True, True, True, True
        if self.rect.centerx <= self.image.get_width() / 2:
            can_left = False

        if self.rect.centerx >= SCREEN_WIDTH - self.image.get_width() / 2:
            can_right = False

        if self.rect.centery <= self.image.get_height() / 2:
            can_up = False

        if self.rect.centery >= SCREEN_HEIGHT - self.image.get_height() / 2:
            can_down = False

        
        self.direction.x = can_right * int(keys[pygame.K_RIGHT]) - can_left * int(keys[pygame.K_LEFT])
        self.direction.y = can_down * int(keys[pygame.K_DOWN]) - can_up * int(keys[pygame.K_UP])
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
        enemy_width = enemy_surface.get_size()[0]
        position = (random.randint(int(enemy_width / 2), SCREEN_WIDTH - int(enemy_width / 2)), 0)
        self.rect = self.image.get_frect(center = position)
        self.direction = pygame.Vector2(0, 1)
        self.speed = 250 + 30 * deltatime

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

class UpgradeIcon(pygame.sprite.Sprite):
    def __init__(self, groups, surface, position):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = position)
        self.life = 0

    def update(self, keys, deltatime):
        if self.life < 5000:
            self.life += 1000 * deltatime
        else:
            self.kill()

def laser_collisions():
    global enemies_destroyed
    mov_spd_flag = False
    att_spd_flag = False
    for laser in laser_sprites:
        collided_enemy = pygame.sprite.spritecollide(laser, enemy_sprites, True, pygame.sprite.collide_mask)
        if collided_enemy:
            laser.kill()
            Explosion(all_sprites, explosion_frames, collided_enemy[0].rect.midtop)
            if random.uniform(0, 1) < mov_spd_rate:
                mov_spd_flag = True
            if random.uniform(0, 1) < att_spd_rate:
                att_spd_flag = True
            
            if mov_spd_flag and not att_spd_flag:
                UpgradeIcon((all_sprites, mov_spd_sprites), mov_spd_surface, collided_enemy[0].rect.center)
            elif att_spd_flag and not mov_spd_flag:
                UpgradeIcon((all_sprites, att_spd_sprites), att_spd_surface, collided_enemy[0].rect.center)
            elif att_spd_flag and mov_spd_flag:
                if random.randint(0, 1):
                    UpgradeIcon((all_sprites, mov_spd_sprites), mov_spd_surface, collided_enemy[0].rect.center)
                else:
                    UpgradeIcon((all_sprites, att_spd_sprites), att_spd_surface, collided_enemy[0].rect.center)

            enemies_destroyed += 1

def player_collisions(high_scores):
    global lives
    global player
    collided_enemy = pygame.sprite.spritecollide(player, enemy_sprites, True, pygame.sprite.collide_mask)
    if collided_enemy:
        damage_sound_effect.play()
        lives -= 1
        if lives == 0:
            player.kill()
            game_over_screen(high_scores)
        Explosion(all_sprites, explosion_frames, collided_enemy[0].rect.center)

    collided_mov_spd = pygame.sprite.spritecollide(player, mov_spd_sprites, True, pygame.sprite.collide_mask)
    if collided_mov_spd:
        upgrade_sound_effect.play()
        if player.speed < 1000:
            player.speed += 25

    collided_att_spd = pygame.sprite.spritecollide(player, att_spd_sprites, True, pygame.sprite.collide_mask)
    if collided_att_spd:
        upgrade_sound_effect.play()
        if player.cooldown_time > 0:
            player.cooldown_time -= 25

def display_game_info(title, info, topleft_point, border = False, color = (230, 230, 230)):
    title_surface = font.render(f"{title}: ", True, color)
    title_rect = title_surface.get_frect(topleft = topleft_point)
    info_surface = font.render(str(info), True, color)
    info_rect = info_surface.get_frect(topleft = title_rect.topright)
    screen.blit(title_surface, title_rect)
    screen.blit(info_surface, info_rect)
    if border:
        pygame.draw.rect(screen, (230, 230, 230), info_rect.inflate(15, 15), 5, 5)
    
def fade(width, height): 
    fade = pygame.Surface((width, height))
    fade.fill((0,0,0))
    for alpha in range(0, 300):
        fade.set_alpha(alpha)
        draw_window()
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)

def game_over_screen(high_scores):
    global running
    global enemies_destroyed
    high_scores = update_high_score(high_scores, enemies_destroyed)
    write_high_scores(join('game_assets', 'high_scores.txt'), high_scores)
    fade(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_over = True
    game_over_text_surface = game_over_font.render('Game Over', True, (255, 0, 0))
    game_over_text_rect = game_over_text_surface.get_frect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
    game_over_info_surface = font.render('Press ESC to exit...', True, (255, 0, 0))
    game_over_info_rect = game_over_info_surface.get_frect(midtop = game_over_text_rect.inflate(0, 30).midbottom)
    screen.fill('black')
    screen.blit(game_over_text_surface, game_over_text_rect)
    screen.blit(game_over_info_surface, game_over_info_rect)
    display_game_info('final score', enemies_destroyed, game_over_info_rect.inflate(0, 30).bottomleft, color=(255, 0 , 0))
    leaderboard_surface = font.render('High scores:', True, (255, 0, 0))
    leaderboard_rect = leaderboard_surface.get_frect(topleft = game_over_info_rect.inflate(0, 5 * font.get_height()).bottomleft)
    screen.blit(leaderboard_surface, leaderboard_rect)
    number = 0
    for score in high_scores:
        display_game_info(number + 1, score, leaderboard_rect.inflate(0, number * (30 + font.get_height())).bottomleft, color=(255, 0 , 0))
        number += 1
    pygame.display.flip()
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
            new_star_rect = pygame.Rect(x, y, star_width, star_height)            
            if not any(new_star_rect.colliderect(existing) for existing in star_positions):
                star_positions.append(new_star_rect)
                break 
            else:
                tries_count += 1
    return star_positions

def draw_window():
    global enemies_destroyed
    global lives
    screen.fill('#2c205a')
    all_sprites.draw(screen)
    display_game_info('score', enemies_destroyed, (10, 10), True)
    display_game_info('lives', lives, (10, font.get_height() + 20))

def read_high_scores(path):
    with open(path, 'r') as file:
        return file.readlines()
    
def write_high_scores(path, high_scores):
    with open(path, 'w') as file:
        for i in range(len(high_scores)):
            file.write(f'{high_scores[i]}\n')


def update_high_score(high_scores, score):
    high_scores_int = [int(hs) for hs in high_scores]
    high_scores_int.append(score)
    high_scores_int = sorted(high_scores_int, reverse=True)
    return high_scores_int[:5]


pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Battle")

all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
star_sprites = pygame.sprite.Group()
att_spd_sprites = pygame.sprite.Group()
mov_spd_sprites = pygame.sprite.Group()

font = pygame.font.Font(join('game_assets', "Sterion-BLLld.ttf"), 30)
game_over_font = pygame.font.Font(join('game_assets', "Sterion-BLLld.ttf"), 100)

laser_surface = pygame.image.load(join('game_assets', 'laser.png')).convert_alpha()
star_surface = pygame.image.load(join('game_assets', 'star.png')).convert_alpha()
att_spd_surface = pygame.image.load(join('game_assets', 'attack_speed_icon.png')).convert_alpha()
mov_spd_surface = pygame.image.load(join('game_assets', 'movement_speed_icon.png')).convert_alpha()
enemy_surface = pygame.image.load(join('game_assets', 'enemy_ship.png')).convert_alpha()
explosion_frames = [pygame.image.load(join('game_assets', 'explosion', f'{i}.png')).convert_alpha() for i in range(1, 13)]

laser_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'laser_sound.mp3'))
laser_sound_effect.set_volume(0.15)
explosion_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'explosion_sound.mp3'))
explosion_sound_effect.set_volume(0.25)
damage_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'damage_sound.mp3'))
background_music = pygame.mixer.Sound(join('game_assets', 'sounds', 'background_music.mp3'))
background_music.set_volume(0.1)
background_music.play(loops= -1)
upgrade_sound_effect = pygame.mixer.Sound(join('game_assets', 'sounds', 'upgrade.mp3'))

star_rects = generate_stars(70)
for rect in star_rects:
    Star((all_sprites, star_sprites), star_surface, rect)
player = Player(all_sprites)
enemies_destroyed = 0
lives = 3
att_spd_rate = 0.3
mov_spd_rate = 0.3
enemy_spawn_cooldown = 2000
enemy_event = pygame.event.custom_type()
increase_enemies_event = pygame.event.custom_type()
pygame.time.set_timer(increase_enemies_event, 3500)
clock = pygame.time.Clock()
high_scores = read_high_scores(join('game_assets', 'high_scores.txt'))
running = True

while running:
    current_time = pygame.time.get_ticks()
    deltatime = clock.tick() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == enemy_event:
            Enemy((all_sprites, enemy_sprites), enemy_surface)
        if event.type == increase_enemies_event and enemy_spawn_cooldown > 100:
            enemy_spawn_cooldown *= 0.92
            pygame.time.set_timer(enemy_event, int(enemy_spawn_cooldown))

    keys = pygame.key.get_pressed()
    all_sprites.update(keys, deltatime)
    laser_collisions()
    player_collisions(high_scores)

    print(f'movement speed: {player.speed}, cooldown: {player.cooldown_time}')

    if running:
        draw_window()
        pygame.display.update()

pygame.quit()
