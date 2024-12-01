import unittest
from ChessCoordinateTraining.src.core.game_logic import GameState
from ChessCoordinateTraining.src.core.stats import GameSession
from datetime import datetime


class TestGameIntegration(unittest.TestCase):
    """Integration tests for game components."""

    def setUp(self):
        self.game_state = GameState()
        self.game_session = GameSession()

    def test_complete_game_flow(self):
        """Test complete game flow with multiple components."""
        # Start game
        self.game_state.start_game()

        # Simulate some moves
        for _ in range(5):
            # Generate new coordinate
            algebraic, col, row = self.game_state.board.generate_coordinate()

            # Simulate correct click
            click_x = col * self.game_state.board._config.TILE_SIZE + 5
            click_y = row * self.game_state.board._config.TILE_SIZE + 5

            # Record attempt
            is_correct = self.game_state.board.validate_click(click_x, click_y)
            self.game_session.record_attempt(is_correct, 0.5)

        # End game
        self.game_state.end_game()

        # Verify final state
        self.assertFalse(self.game_state.is_active)
        self.assertGreater(self.game_session.correct_clicks, 0)

    def test_game_state_with_statistics(self):
        """Test integration between game state and statistics tracking."""
        self.game_state.start_game()

        # Simulate correct and incorrect moves
        algebraic, col, row = self.game_state.board.generate_coordinate()

        # Correct move
        click_x = col * self.game_state.board._config.TILE_SIZE + 5
        click_y = row * self.game_state.board._config.TILE_SIZE + 5
        self.game_session.record_attempt(True, 0.5)

        # Incorrect move
        wrong_x = (col + 1) * self.game_state.board._config.TILE_SIZE
        wrong_y = (row + 1) * self.game_state.board._config.TILE_SIZE
        self.game_session.record_attempt(False, 0.5)

        stats = self.game_session.get_session_stats()
        self.assertEqual(stats['correct'], 1)
        self.assertEqual(stats['wrong'], 1)
        self.assertAlmostEqual(stats['accuracy'], 50.0)

    def test_board_perspective_changes(self):
        """Test integration of board perspective changes with game state."""
        self.game_state.start_game()

        # Record initial coordinate
        initial_coord, col, row = self.game_state.board.generate_coordinate()

        # Flip board
        self.game_state.board.flip_perspective()

        # Verify coordinate translation still works
        click_x = (7 - col) * self.game_state.board._config.TILE_SIZE + 5
        click_y = (7 - row) * self.game_state.board._config.TILE_SIZE + 5

        self.assertTrue(self.game_state.board.validate_click(click_x, click_y))

    def test_board_perspective_multiple_flips(self):
        """Test coordinate validation through multiple perspective changes."""
        self.game_state.start_game()

        # Generate initial coordinate
        initial_coord, col, row = self.game_state.board.generate_coordinate()

        # Test original perspective
        click_x = col * self.game_state.board._config.TILE_SIZE + 5
        click_y = row * self.game_state.board._config.TILE_SIZE + 5
        self.assertTrue(self.game_state.board.validate_click(click_x, click_y))

        # Test flipped perspective
        self.game_state.board.flip_perspective()
        click_x = (7 - col) * self.game_state.board._config.TILE_SIZE + 5
        click_y = (7 - row) * self.game_state.board._config.TILE_SIZE + 5
        self.assertTrue(self.game_state.board.validate_click(click_x, click_y))

        # Test returning to original perspective
        self.game_state.board.flip_perspective()
        click_x = col * self.game_state.board._config.TILE_SIZE + 5
        click_y = row * self.game_state.board._config.TILE_SIZE + 5
        self.assertTrue(self.game_state.board.validate_click(click_x, click_y))

    def test_game_session_persistence(self):
        """Test integration between game session and performance tracking."""
        # Simulate multiple game sessions
        for _ in range(3):
            self.game_state.start_game()
            self.game_session.record_attempt(True, 0.5)
            self.game_session.record_attempt(False, 0.5)
            self.game_state.end_game()

        # Verify session history
        stats = self.game_session.get_session_stats()
        self.assertEqual(self.game_session.correct_clicks, 3)
        self.assertEqual(self.game_session.wrong_clicks, 3)


if __name__ == '__main__':
    unittest.main()
