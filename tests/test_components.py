import unittest
import tkinter as tk
from ChessCoordinateTraining.src.ui.components import UIConfig, ChessboardCanvas, CoordinateDisplay


class TestUIComponents(unittest.TestCase):
    """Test suite for UI components."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        cls.root = tk.Tk()
        cls.config = UIConfig()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        cls.root.destroy()

    def test_chessboard_canvas(self):
        """Test ChessboardCanvas initialization and methods."""
        canvas = ChessboardCanvas(self.root, self.config)

        # Test canvas dimensions
        expected_width = self.config.GRID_SIZE * self.config.TILE_SIZE
        expected_height = expected_width + 40  # Including space for file letters
        self.assertEqual(canvas.board_width, expected_width)
        self.assertEqual(canvas.total_height, expected_height)

        # Test coordinate toggling
        self.assertFalse(canvas.coordinates_visible)
        canvas.toggle_coordinates(True)
        self.assertTrue(canvas.coordinates_visible)

    def test_coordinate_display(self):
        """Test CoordinateDisplay initialization and updates."""
        display = CoordinateDisplay(self.root, self.config)

        # Test initial state
        self.assertEqual(display.label.cget("text"), "Click Start to begin")

        # Test text update
        test_coord = "E4"
        display.update_text(test_coord)
        self.assertEqual(display.label.cget("text"), test_coord)