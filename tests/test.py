import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ChessCoordinateTraining.chessboard import ChessCoordinatesGame


class TestChessCoordinatesGame(unittest.TestCase):
    """
    Comprehensive test suite for the Chess Coordinates Game application.
    Tests core functionality, game logic, and UI components.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        matplotlib.use('Agg')
        matplotlib.font_manager.USE_FONTCONFIG = False

        # Mock all messagebox functions to prevent popups
        messagebox.showinfo = MagicMock()
        messagebox.showerror = MagicMock()
        messagebox.showwarning = MagicMock()
        messagebox.askokcancel = MagicMock(return_value=True)

    def setUp(self):
        """Set up test environment before each test."""
        # Create root window with withdraw to prevent it from showing
        self.root = tk.Tk()
        self.root.withdraw()

        # Mock FigureCanvasTkAgg
        self.canvas_patcher = patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg', autospec=True)
        self.mock_canvas = self.canvas_patcher.start()

        # Configure mock canvas
        mock_canvas_instance = MagicMock()
        mock_canvas_instance.get_width_height.return_value = (800, 600)
        self.mock_canvas.return_value = mock_canvas_instance

        # Create game instance with the mocked canvas and suppressed popups
        with patch('tkinter.messagebox.showinfo'), \
                patch('tkinter.messagebox.showerror'), \
                patch('tkinter.messagebox.showwarning'), \
                patch('tkinter.messagebox.askokcancel', return_value=True):
            self.game = ChessCoordinatesGame()

        # Configure initial game state
        self.game.is_white_perspective = True
        self.game.coordinates_visible = False
        self.game.is_game_active = False

    def tearDown(self):
        """Clean up after each test."""
        try:
            plt.close('all')
            self.canvas_patcher.stop()

            # Handle Tkinter cleanup
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.update()
                self.root.destroy()
        except tk.TclError:
            pass  # Ignore errors if window is already destroyed

    def test_initial_game_state(self):
        """Test the initial state of the game after instantiation."""
        self.assertTrue(self.game.is_white_perspective)
        self.assertFalse(self.game.coordinates_visible)
        self.assertFalse(self.game.is_game_active)
        self.assertEqual(self.game.correct_clicks, 0)
        self.assertEqual(self.game.wrong_clicks, 0)
        self.assertEqual(self.game.total_response_time, 0)

    def test_flip_board(self):
        """Test board perspective flipping functionality."""
        initial_perspective = self.game.is_white_perspective
        self.game.flip_board()
        self.assertNotEqual(initial_perspective, self.game.is_white_perspective)

    def test_coordinate_generation(self):
        """Test random coordinate generation and validity."""
        algebraic, col, row = self.game.generate_random_coordinate()

        # Check coordinate format
        self.assertTrue(len(algebraic) == 2)
        self.assertTrue('A' <= algebraic[0] <= 'H')
        self.assertTrue(1 <= int(algebraic[1]) <= 8)

    def test_coordinate_conversion(self):
        """Test coordinate text generation for various board positions."""
        self.game.is_white_perspective = True
        result = self.game.get_coordinate_text(0, 0)
        self.assertEqual(result, "A8")

    def test_score_calculation(self):
        """Test score calculation with various game scenarios."""
        # Test perfect score scenario
        self.game.correct_clicks = 10
        self.game.wrong_clicks = 0
        self.game.total_response_time = 10  # 1 second per click
        score1 = self.game.calculate_score()

        # Test with some mistakes
        self.game.correct_clicks = 10
        self.game.wrong_clicks = 5
        self.game.total_response_time = 15
        score2 = self.game.calculate_score()

        # Test with slow responses
        self.game.correct_clicks = 10
        self.game.wrong_clicks = 0
        self.game.total_response_time = 30
        score3 = self.game.calculate_score()

        # Verify scoring logic
        self.assertTrue(score1 > score2)  # Perfect score should be higher than with mistakes
        self.assertTrue(score1 > score3)  # Fast responses should score higher than slow ones
        self.assertTrue(score2 != 0)  # Non-zero score for partial success

    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('json.dump')
    def test_save_stats(self, mock_json_dump, mock_filedialog):
        """Test statistics saving functionality."""
        # Setup test data
        self.game.score_history = [100, 200, 300]
        self.game.accuracy_history = [80, 85, 90]
        mock_filedialog.return_value = "test_stats.json"

        # Test save functionality
        self.game.save_stats()

        # Verify json.dump was called with correct data structure
        mock_json_dump.assert_called_once()
        called_data = mock_json_dump.call_args[0][0]
        self.assertIn('score_history', called_data)
        self.assertIn('accuracy_history', called_data)
        self.assertIn('timestamp', called_data)

    @patch('tkinter.filedialog.askopenfilename')
    def test_load_stats(self, mock_filedialog):
        """Test statistics loading functionality."""
        # Prepare test data
        test_data = {
            'score_history': [100, 200, 300],
            'accuracy_history': [80, 85, 90],
            'correct_clicks_history': [10, 15, 20],
            'wrong_clicks_history': [2, 3, 1],
            'avg_time_history': [1.5, 1.3, 1.2],
            'fastest_time_history': [0.8, 0.7, 0.9],
            'slowest_time_history': [2.1, 2.0, 1.8],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Mock file operations
        mock_filedialog.return_value = "test_stats.json"
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_data))):
            self.game.load_stats()

        # Verify loaded data
        self.assertEqual(self.game.score_history, test_data['score_history'])
        self.assertEqual(self.game.accuracy_history, test_data['accuracy_history'])

    def test_game_timer(self):
        """Test game timer functionality and game state transitions."""
        # Mock time.time to control timing
        with patch('time.time', return_value=100.0):
            # Store initial coordinate text
            initial_coord = self.game.coord_label.cget("text")

            # Start the game
            self.game.start_timer()
            self.assertTrue(self.game.is_game_active)
            self.assertIsNotNone(self.game.current_coordinate)

            # Simulate game end by directly calling the timer completion
            self.game.is_game_active = False
            self.game.coord_label.config(text="Game Over!")

            # Verify final state
            self.assertFalse(self.game.is_game_active)
            self.assertEqual(self.game.coord_label.cget("text"), "Game Over!")

    def test_coordinate_click_handling(self):
        """Test click handling and score updating."""
        self.game.is_game_active = True
        self.game.current_coordinate = (3, 3)  # Example coordinate D5

        # Simulate correct click
        event = MagicMock()
        event.x = 3 * self.game.TILE_SIZE + self.game.TILE_SIZE // 2
        event.y = 3 * self.game.TILE_SIZE + self.game.TILE_SIZE // 2

        initial_correct = self.game.correct_clicks
        self.game.check_coordinate(event)
        self.assertEqual(self.game.correct_clicks, initial_correct + 1)

        # Simulate wrong click
        event.x = 0
        event.y = 0
        initial_wrong = self.game.wrong_clicks
        self.game.check_coordinate(event)
        self.assertEqual(self.game.wrong_clicks, initial_wrong + 1)


def main():
    """
    Main test runner function.
    Executes the test suite with verbose output.
    """
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
