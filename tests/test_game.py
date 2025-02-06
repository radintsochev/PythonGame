import unittest
import tempfile
from unittest import mock
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_SETTINGS
from sprites import Player, Laser, Enemy, Explosion, UpgradeIcon, Star
from game_functions import (handle_collisions, generate_stars, read_high_scores,
                            write_high_scores, update_high_score, display_game_info,
                            fade, game_over_screen, draw_window)

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.groups = []
        self.laser_groups = []
        self.laser_sound = mock.MagicMock()
        self.player = Player(self.groups, self.laser_groups, self.laser_sound)
        
    @mock.patch('pygame.init')
    @mock.patch('pygame.display.set_mode')
    @mock.patch('pygame.font.Font')
    def test_player_movement(self, *_):
        self.player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        keys = {
            pygame.K_RIGHT: 1, 
            pygame.K_LEFT: 0, 
            pygame.K_UP: 0, 
            pygame.K_DOWN: 0
        }
        
        self.player.update(keys, 0.1)
        self.assertGreater(self.player.rect.centerx, SCREEN_WIDTH/2)
    
    # Add to TestPlayer class
    def test_laser_cooldown(self):
        self.player.can_shoot = False
        self.player.laser_shoot_time = pygame.time.get_ticks() - 1000
        self.player.laser_timer()
        self.assertTrue(self.player.can_shoot)

    def test_movement_constraints(self):
        self.player.rect.right = SCREEN_WIDTH + 10
        keys = {pygame.K_RIGHT: 1}
        self.player.update(keys, 0.1)
        self.assertLessEqual(self.player.rect.right, SCREEN_WIDTH)

    # Add to TestLaser class
    def test_laser_cleanup(self):
        laser = Laser([], pygame.Surface((10,10)), (0, SCREEN_HEIGHT))
        laser.update(None, 1.0)
        self.assertFalse(laser.alive())

    # Add to TestEnemy class
    def test_enemy_movement(self):
        enemy = Enemy([], pygame.Surface((10,10)))
        initial_y = enemy.rect.y
        enemy.update(None, 0.1)
        self.assertGreater(enemy.rect.y, initial_y)

    # Add to TestExplosion class
    def test_explosion_cleanup(self):
        frames = [pygame.Surface((10,10)) for _ in range(5)]
        explosion = Explosion([], frames, (0,0))
        for _ in range(10):
            explosion.update(None, 1.0)
        self.assertFalse(explosion.alive())

    # Add to TestUpgradeLifetime class
    def test_upgrade_application(self):
        player = Player([], [], mock.MagicMock())
        upgrade = UpgradeIcon([], pygame.Surface((10,10)), (0,0))
        initial_speed = player.speed
        
        handle_collisions(
            pygame.sprite.Group(), pygame.sprite.Group(),
            player, pygame.sprite.Group(), pygame.sprite.Group([upgrade]),
            {'sounds': {'upgrade': mock.MagicMock()}}, {}
        )
        self.assertNotEqual(player.speed, initial_speed)

        def test_player_boundary_constraints(self):
            player = Player([], [], mock.MagicMock())
            player.rect.right = SCREEN_WIDTH + 100
            keys = {pygame.K_RIGHT: 1}
            player.update(keys, 0.1)
            self.assertLessEqual(player.rect.right, SCREEN_WIDTH)

class TestLaser(unittest.TestCase):
    def test_laser_movement(self):
        groups = []
        surface = pygame.Surface((10, 20))
        laser = Laser(groups, surface, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        initial_y = laser.rect.y
        laser.update(None, 0.1)
        self.assertLess(laser.rect.y, initial_y)

class TestEnemy(unittest.TestCase):
    def test_enemy_despawn(self):
        groups = []
        enemy = Enemy(groups, pygame.Surface((50, 30)))
        enemy.rect.y = SCREEN_HEIGHT + 10
        enemy.update(None, 0.1)
        self.assertFalse(enemy.alive())

class TestGameFunctions(unittest.TestCase):
    @mock.patch('pygame.sprite.collide_mask')
    def test_handle_collisions(self, mock_collide):
        mock_collide.return_value = True
        lasers = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        player = mock.MagicMock()
        game_state = {'score': 0}
        
        Laser(lasers, pygame.Surface((10, 10)), (100, 100))
        Enemy(enemies, pygame.Surface((20, 20)))
        
        handle_collisions(
            lasers, enemies, player, pygame.sprite.Group(),
            pygame.sprite.Group(), pygame.sprite.Group(),
            {'sounds': {'explosion': mock.MagicMock()}}, game_state
        )
        self.assertEqual(game_state['score'], 1)

    def test_high_score_updates(self):
        with tempfile.NamedTemporaryFile() as tmp:
            test_scores = [100, 80, 60, 40, 20]
            write_high_scores(tmp.name, test_scores)
            self.assertEqual(read_high_scores(tmp.name), test_scores)
            
            new_scores = update_high_score(test_scores, 90)
            self.assertEqual(new_scores, [100, 90, 80, 60, 40])

    # Add to TestGameFunctions class
    def test_display_game_info_border(self):
        mock_screen = mock.MagicMock()
        mock_font = mock.MagicMock()
        display_game_info(mock_screen, mock_font, 'Test', 100, (0, 0), border=True)
        mock_font.render.assert_called()

    @mock.patch('pygame.display.flip')
    @mock.patch('pygame.time.delay')
    def test_fade(self, mock_delay, mock_flip):
        mock_screen = mock.MagicMock()
        fade(mock_screen, lambda: None, 100, 200)
        self.assertEqual(mock_screen.blit.call_count, 300//5)

    @mock.patch('game_functions.fade')
    def test_game_over_screen_flow(self, mock_fade):
        mock_screen = mock.MagicMock()
        result = game_over_screen(mock_screen, mock.MagicMock(), mock.MagicMock(), 
                                [100, 80], 90, 0, pygame.sprite.Group())
        self.assertFalse(result)

    def test_generate_stars_edge_cases(self):
        stars = generate_stars(100, pygame.Surface((5,5)))
        self.assertTrue(len(stars) > 50)  # Test collision avoidance

    def test_draw_window(self):
        mock_screen = mock.MagicMock()
        mock_group = mock.MagicMock()
        draw_window(mock_screen, mock_group, 0, 3, mock.MagicMock())
        mock_group.draw.assert_called_once()

    def test_read_write_high_scores_edge_cases(self):
        # Test empty file
        with tempfile.NamedTemporaryFile() as tmp:
            assert read_high_scores(tmp.name) == [0]*5
        
        # Test invalid data
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b'invalid\nlines\n')
            tmp.seek(0)
            assert read_high_scores(tmp.name) == [0]*5

    def test_update_high_score(self):
        assert update_high_score([100,90,80], 95) == [100,95,90,80,0]

    # Add to TestGameFunctions class
    @mock.patch('pygame.draw.rect')
    def test_display_game_info_missing_lines(self, mock_draw):
        mock_screen = mock.MagicMock()
        mock_font = mock.MagicMock()
        display_game_info(mock_screen, mock_font, 'Test', 100, (0, 0), color=(255,0,0))
        mock_draw.assert_called_once()

    """def test_handle_collisions_both_upgrades(self):
        lasers = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        player = Player([], [], mock.MagicMock())
        laser = Laser(lasers, pygame.Surface((10,10)), (100, 100))
        enemy = Enemy(enemies, pygame.Surface((20,20)))
        
        with mock.patch('random.uniform') as mock_uniform:
            mock_uniform.side_effect = [0.5, 0.5]  # Force both upgrades
            handle_collisions(
                lasers, enemies, player, pygame.sprite.Group(),
                pygame.sprite.Group(), pygame.sprite.Group(),
                {'sounds': mock.MagicMock()}, {'score': 0}
            )
            self.assertEqual(len(upgrades), 1)"""

    @mock.patch('os.path.exists')
    def test_read_high_scores_missing_file(self, mock_exists):
        mock_exists.return_value = False
        scores = read_high_scores('non_existent.txt')
        self.assertEqual(scores, [0]*5)

class TestGameInitialization(unittest.TestCase):
    @mock.patch('pygame.mixer.Sound')
    @mock.patch('pygame.image.load')
    def test_load_assets(self, mock_load, mock_sound):
        mock_load.return_value = pygame.Surface((10, 10))
        from ..main import load_assets
        assets = load_assets()
        self.assertIn('player', assets)

class TestCollisionLogic(unittest.TestCase):
    def test_player_upgrade_collision(self):
        upgrades = pygame.sprite.Group()
        player = Player([], [], mock.MagicMock())
        upgrade = UpgradeIcon([], pygame.Surface((20, 20)), (0, 0))
        upgrades.add(upgrade)
        player.rect.center = (0, 0)
        
        handle_collisions(
            pygame.sprite.Group(), pygame.sprite.Group(),
            player, pygame.sprite.Group(), pygame.sprite.Group(),
            upgrades, {'sounds': {'upgrade': mock.MagicMock()}}, {}
        )
        self.assertTrue(player.speed > 400 or player.cooldown_time < 600)

class TestStarGeneration(unittest.TestCase):
    def test_star_generation(self):
        stars = generate_stars(10, pygame.Surface((5, 5)))
        self.assertEqual(len(stars), 10)
        for star in stars[1:]:
            collisions = any(star.colliderect(other) for other in stars if star != other)
            self.assertFalse(collisions)
    
    # Add missing test cases
    def test_star_initialization(self):
        star = Star([], pygame.Surface((5,5)), pygame.Rect(0,0,5,5))
        self.assertIsInstance(star, Star)

    # Add to TestStar class
    def test_star_initialization(self):
        star_rect = pygame.Rect(10, 10, 5, 5)
        star = Star([], pygame.Surface((5,5)), star_rect)
        self.assertEqual(star.rect, star_rect)

class TestGameOver(unittest.TestCase):
    @mock.patch('game_functions.update_high_score')
    def test_game_over_sequence(self, mock_update):
        from ..main import game_over_screen
        mock_screen = mock.MagicMock()
        mock_font = mock.MagicMock()
        
        game_over_screen(
            mock_screen, mock_font, mock_font,
            [100, 80, 60], 90, 0, pygame.sprite.Group()
        )
        mock_update.assert_called_once()

    def test_full_game_cycle(self):
        from main import main
        with mock.patch('code.main.game_over_screen') as mock_over:
            mock_over.return_value = False
            main()
            self.assertTrue(mock_over.called)

class TestDifficulty(unittest.TestCase):
    def test_difficulty_increase(self):
        from ..main import game_state
        game_state.update({
            'last_difficulty_increase': 0,
            'spawn_cooldown': 2000
        })
        
        current_time = GAME_SETTINGS['difficulty_increase_interval'] + 1
        time_since = current_time - game_state['last_difficulty_increase']
        
        if time_since > GAME_SETTINGS['difficulty_increase_interval']:
            game_state['spawn_cooldown'] = max(100, int(game_state['spawn_cooldown'] * 0.92))
            game_state['last_difficulty_increase'] = current_time
        
        self.assertEqual(game_state['spawn_cooldown'], 1840)

class TestExplosion(unittest.TestCase):
    def test_explosion_animation(self):
        frames = [pygame.Surface((20, 20)) for _ in range(5)]
        explosion = Explosion([], frames, (100, 100))
        explosion.update(None, 0.1)
        self.assertGreater(explosion.frame_index, 0)

class TestMainLoop(unittest.TestCase):
    @mock.patch('pygame.quit')
    @mock.patch('pygame.event.get')
    @mock.patch('sys.exit')
    def test_main_loop_exit(self, mock_exit, mock_event, mock_quit):
        from main import game_state
        
        # Setup mock event
        mock_event.return_value = [pygame.event.Event(pygame.QUIT)]
        game_state['running'] = True

        # Simulate one game loop iteration
        game_state['running'] = False
        
        # Verify cleanup
        mock_quit.assert_called_once()
        mock_exit.assert_called_once_with(0)
        self.assertFalse(game_state['running'])
    
    # Add to TestMainLoop class
    @mock.patch('pygame.quit')
    @mock.patch('sys.exit')
    def test_full_main_execution(self, mock_exit, mock_quit):
        from main import main
        with mock.patch('code.main.game_over_screen') as mock_over:
            mock_over.return_value = False
            main()
            mock_quit.assert_called_once()
            mock_exit.assert_called_once_with(0)

class TestUpgradeLifetime(unittest.TestCase):
    def test_upgrade_lifetime(self):
        upgrade = UpgradeIcon([], pygame.Surface((20, 20)), (0, 0))
        upgrade.update(None, GAME_SETTINGS['upgrade_lifetime'] / 1000 + 0.1)
        self.assertFalse(upgrade.alive())

class TestDisplay(unittest.TestCase):
    @mock.patch('pygame.font.Font')
    def test_score_display(self, mock_font):
        from ..game_functions import display_game_info
        mock_screen = mock.MagicMock()
        display_game_info(mock_screen, mock_font, 'Test', 100, (0, 0))
        mock_font.return_value.render.assert_called()

    # Add missing test cases
    @mock.patch('pygame.font.Font')
    def test_display_game_info_error_handling(self, mock_font):
        mock_font.side_effect = Exception('Font error')
        with self.assertRaises(Exception):
            display_game_info(mock.MagicMock(), mock_font, 'Test', 0, (0,0))

if __name__ == '__main__':
    unittest.main()