"""
This module contains the main execution code for the project.
"""
import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PATHS, GAME_SETTINGS
from sprites import Player, Enemy, Star
from game_functions import generate_stars, read_high_scores
from game_functions import handle_collisions, game_over_screen, draw_window

# Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Battle")
clock = pygame.time.Clock()
font = pygame.font.Font(PATHS['fonts']['regular'], 30)
game_over_font = pygame.font.Font(PATHS['fonts']['game_over'], 100)

def load_assets():
    '''
    This func loads the assets from the config file.
    '''
    assets_to_return = {
        'player': pygame.image.load(PATHS['player']).convert_alpha(),
        'laser': pygame.image.load(PATHS['laser']).convert_alpha(),
        'enemy': pygame.image.load(PATHS['enemy']).convert_alpha(),
        'star': pygame.image.load(PATHS['star']).convert_alpha(),
        'explosion_frames': [pygame.image.load(p) for p in PATHS['explosion']],
        'mov_spd_icon': pygame.image.load(PATHS['mov_spd_icon']).convert_alpha(),
        'att_spd_icon': pygame.image.load(PATHS['att_spd_icon']).convert_alpha(),
        'sounds': {
            'laser': pygame.mixer.Sound(PATHS['sounds']['laser']),
            'explosion': pygame.mixer.Sound(PATHS['sounds']['explosion']),
            'damage': pygame.mixer.Sound(PATHS['sounds']['damage']),
            'background': pygame.mixer.Sound(PATHS['sounds']['background']),
            'upgrade': pygame.mixer.Sound(PATHS['sounds']['upgrade']),
        },
        'fonts': {
            'regular': pygame.font.Font(PATHS['fonts']['regular'], 30),
            'game_over': pygame.font.Font(PATHS['fonts']['game_over'], 100)
        }
    }
    assets_to_return['sounds']['laser'].set_volume(0.15)
    assets_to_return['sounds']['explosion'].set_volume(0.25)
    assets_to_return['sounds']['background'].set_volume(0.1)
    return assets_to_return

# Game state
game_state = {
        'score': 0,
        'lives': 3,
        'running': True,
        'spawn_cooldown': GAME_SETTINGS['initial_spawn_cooldown'],
        'last_difficulty_increase': 0,
    }

# Sprite groups
all_sprites = pygame.sprite.Group()
lasers = pygame.sprite.Group()
enemies = pygame.sprite.Group()
explosions = pygame.sprite.Group()
upgrades = pygame.sprite.Group()
stars = pygame.sprite.Group()

# Load assets and create entities
assets = load_assets()
player = Player(all_sprites, [all_sprites, lasers], assets['sounds']['laser'])
assets['sounds']['background'].play(loops=-1)

# Generate stars
star_rects = generate_stars(GAME_SETTINGS['num_stars'], assets['star'])
for rect in star_rects:
    Star(stars, assets['star'], rect)

# Load high scores
high_scores = read_high_scores(PATHS['high_scores'])


# Main game loop
while game_state['running']:
    dt = clock.tick(60) / 1000
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state['running'] = False

    # Progressive difficulty
    time_since_last_increase = current_time - game_state['last_difficulty_increase']
    if time_since_last_increase > GAME_SETTINGS['difficulty_increase_interval']:
        game_state['spawn_cooldown'] = max(100, int(game_state['spawn_cooldown'] * 0.92))
        game_state['last_difficulty_increase'] = current_time

    # Enemy spawning
    if current_time % game_state['spawn_cooldown'] < dt * 1000:
        Enemy([all_sprites, enemies], assets['enemy'])

    # Update
    all_sprites.update(keys, dt)
    # Collision handling
    handle_collisions(lasers, enemies, player, all_sprites,
                      explosions, upgrades, assets, game_state)
    # Check game over
    if game_state['lives'] <= 0:
        game_state['running'] = game_over_screen(
            screen,
            font,
            game_over_font,
            high_scores,
            game_state['score'],
            game_state['lives'],
            all_sprites
        )
        game_state['running'] = False

    # Drawing
    screen.fill('#2c205a')  # Original background color
    stars.draw(screen)      # Draw stars first
    all_sprites.draw(screen)

    # UI
    draw_window(screen, all_sprites, game_state['score'], game_state['lives'], font)
    pygame.display.update()

pygame.quit()
sys.exit()

if __name__ == "__main__":
    main()
