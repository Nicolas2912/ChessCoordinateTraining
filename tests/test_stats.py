import unittest
from datetime import datetime
from ChessCoordinateTraining.src.core.stats import GameSession, PerformanceTracker


class TestGameSession(unittest.TestCase):
    """Test suite for GameSession class."""

    def setUp(self):
        self.session = GameSession()

    def test_session_reset(self):
        """Test session reset functionality."""
        # Add some data
        self.session.correct_clicks = 10
        self.session.wrong_clicks = 5
        self.session.total_response_time = 15.5

        # Reset session
        self.session.reset()

        # Verify reset state
        self.assertEqual(self.session.correct_clicks, 0)
        self.assertEqual(self.session.wrong_clicks, 0)
        self.assertEqual(self.session.total_response_time, 0.0)
        self.assertEqual(self.session.fastest_response, float('inf'))
        self.assertEqual(self.session.slowest_response, 0.0)

    def test_record_attempt(self):
        """Test attempt recording and statistics calculation."""
        # Record correct attempts
        self.session.record_attempt(True, 1.0)
        self.session.record_attempt(True, 0.5)

        # Record wrong attempt
        self.session.record_attempt(False, 0.0)

        # Verify statistics
        self.assertEqual(self.session.correct_clicks, 2)
        self.assertEqual(self.session.wrong_clicks, 1)
        self.assertEqual(self.session.total_response_time, 1.5)
        self.assertEqual(self.session.fastest_response, 0.5)
        self.assertEqual(self.session.slowest_response, 1.0)


class TestPerformanceTracker(unittest.TestCase):
    """Test suite for PerformanceTracker class."""

    def setUp(self):
        self.tracker = PerformanceTracker()

    def test_record_session(self):
        """Test session recording and history tracking."""
        # Create test session
        session = GameSession()
        session.record_attempt(True, 1.0)
        session.record_attempt(True, 0.5)
        session.record_attempt(False, 0.0)

        # Record session
        self.tracker.record_session(100, session)

        # Verify history
        self.assertEqual(len(self.tracker.score_history), 1)
        self.assertEqual(self.tracker.score_history[0], 100)
        self.assertEqual(len(self.tracker.accuracy_history), 1)
        self.assertAlmostEqual(self.tracker.accuracy_history[0], 66.67, places=2)