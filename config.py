import os
from os.path import join

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

PATHS = {
    'player': join('game_assets', 'player_ship.png'),
    'laser': join('game_assets', 'laser.png'),
    'enemy': join('game_assets', 'enemy_ship.png'),
    'explosion': [join('game_assets', 'explosion', f'{i}.png') for i in range(1, 13)],
    'star': join('game_assets', 'star.png'),
    'att_spd_icon': join('game_assets', 'attack_speed_icon.png'),
    'mov_spd_icon': join('game_assets', 'movement_speed_icon.png'),
    'sounds': {
        'laser': join('game_assets', 'sounds', 'laser_sound.mp3'),
        'explosion': join('game_assets', 'sounds', 'explosion_sound.mp3'),
        'damage': join('game_assets', 'sounds', 'damage_sound.mp3'),
        'background': join('game_assets', 'sounds', 'background_music.mp3'),
        'upgrade': join('game_assets', 'sounds', 'upgrade.mp3'),
    },
    'fonts': {
        'regular': join('game_assets', "Sterion-BLLld.ttf"),
        'game_over': join('game_assets', "Sterion-BLLld.ttf"),
    },
    'high_scores': join('game_assets', 'high_scores.txt')
}

GAME_SETTINGS = {
    'mov_spd_rate': 0.3,
    'att_spd_rate': 0.3,
    'initial_spawn_cooldown': 2000,
    'difficulty_increase_interval': 3500,
    'num_stars': 70,
    'star_spawn_tries': 50,
    'upgrade_lifetime': 5000,
    'max_player_speed': 1000,
    'min_attack_cooldown': 100
}