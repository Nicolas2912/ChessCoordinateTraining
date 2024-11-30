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


if __name__ == '__main__':
    unittest.main(verbosity=2)