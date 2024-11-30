import unittest
from unittest.mock import MagicMock, patch
from ChessCoordinateTraining.src.core.game_logic import ChessBoardState, GameState, GameConfig


class TestChessBoardState(unittest.TestCase):
    """Test suite for ChessBoardState class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.board = ChessBoardState()

    def test_initial_state(self):
        """Test initial board state configuration."""
        self.assertTrue(self.board.is_white_perspective)
        self.assertIsNone(self.board.current_coordinate)

    def test_flip_perspective(self):
        """Test board perspective flipping functionality."""
        initial_perspective = self.board.is_white_perspective
        self.board.flip_perspective()
        self.assertNotEqual(initial_perspective, self.board.is_white_perspective)

    def test_generate_coordinate(self):
        """Test random coordinate generation and validity."""
        algebraic, col, row = self.board.generate_coordinate()

        # Check coordinate format
        self.assertEqual(len(algebraic), 2)
        self.assertTrue('A' <= algebraic[0] <= 'H')
        self.assertTrue(1 <= int(algebraic[1]) <= 8)

        # Verify column and row are within bounds
        self.assertTrue(0 <= col < self.board._config.GRID_SIZE)
        self.assertTrue(0 <= row < self.board._config.GRID_SIZE)

    def test_validate_click(self):
        """Test click validation for different board positions."""
        # Generate a target coordinate
        _, col, row = self.board.generate_coordinate()

        # Test correct click
        click_x = col * self.board._config.TILE_SIZE + self.board._config.TILE_SIZE // 2
        click_y = row * self.board._config.TILE_SIZE + self.board._config.TILE_SIZE // 2
        self.assertTrue(self.board.validate_click(click_x, click_y))

        # Test incorrect click
        wrong_x = (col + 1) * self.board._config.TILE_SIZE
        wrong_y = (row + 1) * self.board._config.TILE_SIZE
        self.assertFalse(self.board.validate_click(wrong_x, wrong_y))


class TestGameState(unittest.TestCase):
    """Test suite for GameState class."""

    def setUp(self):
        self.game_state = GameState()

    def test_game_lifecycle(self):
        """Test complete game lifecycle."""
        # Initial state
        self.assertFalse(self.game_state.is_active)
        self.assertIsNone(self.game_state.last_coordinate_time)

        # Start game
        self.game_state.start_game()
        self.assertTrue(self.game_state.is_active)

        # End game
        self.game_state.end_game()
        self.assertFalse(self.game_state.is_active)
        self.assertIsNone(self.game_state.last_coordinate_time)