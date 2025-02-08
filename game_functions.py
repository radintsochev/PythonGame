'''
This module contains various game functions for handling collisions, displaying game information, 
fading effects, game over screen, generating stars, drawing the game window,
and managing high scores.
'''
import random
import pygame
from typing import List, Tuple, Callable
from config import GAME_SETTINGS, SCREEN_WIDTH, SCREEN_HEIGHT, PATHS
from sprites import UpgradeIcon, Explosion

def handle_collisions(
    lasers: pygame.sprite.Group,
    enemies: pygame.sprite.Group,
    player: pygame.sprite.Sprite,
    all_sprites: pygame.sprite.Group,
    explosions: pygame.sprite.Group,
    upgrades: pygame.sprite.Group,
    assets: dict,
    game_state: dict
) -> None:
    '''
    Handles collisions between lasers and enemies, player and enemies, and player and upgrades.
    '''
    mov_spd_flag = False
    att_spd_flag = False
    for laser in lasers:
        collided_enemy = pygame.sprite.spritecollide(laser, enemies,
                                        True, pygame.sprite.collide_mask)
        if collided_enemy:
            laser.kill()
            game_state['score'] += 1
            assets['sounds']['explosion'].play()

            # Spawn upgrades
            if random.uniform(0, 1) < GAME_SETTINGS['mov_spd_rate']:
                mov_spd_flag = True
            if random.uniform(0, 1) < GAME_SETTINGS['att_spd_rate']:
                att_spd_flag = True

            if mov_spd_flag and not att_spd_flag:
                UpgradeIcon((all_sprites, upgrades), assets['mov_spd_icon'], collided_enemy[0].rect.center)
            elif att_spd_flag and not mov_spd_flag:
                UpgradeIcon((all_sprites, upgrades), assets['att_spd_icon'], collided_enemy[0].rect.center)
            elif att_spd_flag and mov_spd_flag:
                if random.randint(0, 1):
                    UpgradeIcon((all_sprites, upgrades), assets['mov_spd_icon'], collided_enemy[0].rect.center)
                else:
                    UpgradeIcon((all_sprites, upgrades), assets['att_spd_icon'], collided_enemy[0].rect.center)
            else:
                Explosion([all_sprites, explosions], assets['explosion_frames'], collided_enemy[0].rect.center)

    # Player collisions
    if pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_mask):
        assets['sounds']['damage'].play()
        game_state['lives'] -= 1

    # Upgrade collisions
    for upgrade in pygame.sprite.spritecollide(player, upgrades, True):
        assets['sounds']['upgrade'].play()
        if upgrade.image == assets['mov_spd_icon']:
            # Use the setting from config
            player.speed = min(player.speed + 25, GAME_SETTINGS['max_player_speed'])
        else:
            # Use the setting from config
            player.cooldown_time = max(player.cooldown_time - 25, GAME_SETTINGS['min_attack_cooldown'])

def display_game_info(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title: str,
    info: int,
    topleft_point: Tuple[int, int],
    border: bool = False,
    color: Tuple[int, int, int] = (230, 230, 230)
) -> None:    
    '''
    Displays game information such as score and lives on the screen.
    '''
    title_surface = font.render(f"{title}: ", True, color)
    title_rect = title_surface.get_frect(topleft=topleft_point)
    info_surface = font.render(str(info), True, color)
    info_rect = info_surface.get_frect(topleft=title_rect.topright)
    screen.blit(title_surface, title_rect)
    screen.blit(info_surface, info_rect)
    if border:
        pygame.draw.rect(screen, (230, 230, 230), info_rect.inflate(15, 15), 5, 5)

def fade(
    screen: pygame.Surface,
    draw_window: Callable[[], None],
    width: int,
    height: int
) -> None:
    '''
    Creates a fade effect on the screen.
    '''
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 300):
        fade_surface.set_alpha(alpha)
        draw_window()
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(5)

def game_over_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    game_over_font: pygame.font.Font,
    high_scores: List[int],
    current_score: int,
    lives: int,
    all_sprites: pygame.sprite.Group
) -> bool:
    '''
    Displays the game over screen with final score and high scores.
    '''
    updated_scores = update_high_score(high_scores, current_score)
    write_high_scores(PATHS['high_scores'], updated_scores)

    # Fade effect
    fade(screen, lambda: draw_window(screen, all_sprites, current_score, lives, font), SCREEN_WIDTH, SCREEN_HEIGHT)

    # Game over display
    game_over = True
    screen.fill('black')

    # Game over text
    game_over_text = game_over_font.render('Game Over', True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
    screen.blit(game_over_text, game_over_rect)

    # Instructions
    instruction_text = font.render('Press ESC to exit...', True, (255, 0, 0))
    instruction_rect = instruction_text.get_rect(midtop=game_over_rect.inflate(0, 30).midbottom)
    screen.blit(instruction_text, instruction_rect)

    # Final score
    display_game_info(screen, font, 'Final Score', current_score,
                     instruction_rect.inflate(0, 30).bottomleft, color=(255, 0, 0))

    # High scores
    leaderboard_text = font.render('High Scores:', True, (255, 0, 0))
    leaderboard_rect = leaderboard_text.get_rect(topleft=instruction_rect.inflate(0, 5 * font.get_height()).bottomleft)
    screen.blit(leaderboard_text, leaderboard_rect)

    # Display scores
    y_offset = font.get_height() + 10
    for idx, score in enumerate(updated_scores[:5]):
        display_game_info(screen, font, str(idx+1), score,
                         (leaderboard_rect.left, leaderboard_rect.top + y_offset),
                         color=(255, 0, 0))
        y_offset += font.get_height() + 10

    pygame.display.flip()

    # Wait for input
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
    return True

def generate_stars(
    num_stars: int,
    star_surface: pygame.Surface
) -> List[pygame.Rect]:
    '''
    Generates random positions for stars on the screen.
    '''
    star_width, star_height = star_surface.get_size()
    star_positions = []
    max_tries = 50
    for _ in range(num_stars):
        tries = 0
        while tries < max_tries:
            x = random.randint(0, SCREEN_WIDTH - star_width)
            y = random.randint(0, SCREEN_HEIGHT - star_height)
            new_rect = pygame.Rect(x, y, star_width, star_height)
            if not any(new_rect.colliderect(existing) for existing in star_positions):
                star_positions.append(new_rect)
                break
            tries += 1
    return star_positions

def draw_window(
    screen: pygame.Surface,
    all_sprites: pygame.sprite.Group,
    score: int,
    lives: int,
    font: pygame.font.Font
) -> None:
    '''
    Draws the game window with the current score and lives.
    '''
    display_game_info(screen, font, 'Score', score, (10, 10), True)
    display_game_info(screen, font, 'Lives', lives, (10, font.get_height() + 20))

def read_high_scores(path: str) -> List[int]:
    '''
    Reads high scores from a file.
    '''
    try:
        with open(path, 'r') as file:
            return [int(line.strip()) for line in file.readlines()]
    except:
        return [0] * 5

def write_high_scores(path: str, scores: List[int]) -> None:
    '''
    Writes high scores to a file.
    '''
    with open(path, 'w') as file:
        for score in scores:
            file.write(f"{score}\n")

def update_high_score(current_scores: List[int], new_score: int) -> List[int]:
    '''
    Updates the list of high scores with a new score.
    '''
    updated = current_scores + [new_score]
    return sorted(updated, reverse=True)[:5]