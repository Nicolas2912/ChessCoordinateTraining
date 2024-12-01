from dataclasses import dataclass
from typing import Tuple, Optional, Dict, List
import random
from datetime import datetime


@dataclass
class GameConfig:
    """Configuration settings for the chess coordinates game."""
    GRID_SIZE: int = 8
    TILE_SIZE: int = 60
    MIN_DURATION: int = 5
    MAX_DURATION: int = 60
    DEFAULT_DURATION: int = 30
    BASE_SCORE_PER_CORRECT: int = 100
    PENALTY_PER_WRONG: int = 50
    SPEED_BONUS_MAX: int = 500


class ChessBoardState:
    """
    Manages the state and logic of the chess board, including coordinate generation
    and move validation.
    """

    def __init__(self):
        self.is_white_perspective = True
        self.current_coordinate: Optional[Tuple[int, int]] = None
        self._config = GameConfig()

    def flip_perspective(self) -> None:
        """Toggles the board perspective between white and black sides."""
        self.is_white_perspective = not self.is_white_perspective

    def generate_coordinate(self) -> Tuple[str, int, int]:
        """
        Generates a random chess coordinate for practice.

        Returns:
            Tuple containing:
            - Algebraic notation (e.g., 'E4')
            - Screen column index
            - Screen row index
        """
        file = random.randint(0, self._config.GRID_SIZE - 1)
        rank = random.randint(1, self._config.GRID_SIZE)
        algebraic = f"{chr(ord('A') + file)}{rank}"
        screen_col = file
        screen_row = self._config.GRID_SIZE - rank
        self.current_coordinate = (screen_col, screen_row)
        return algebraic, screen_col, screen_row

    def validate_click(self, click_x: int, click_y: int) -> bool:
        """
        Validates if a clicked position matches the target coordinate.

        Args:
            click_x: Column index of the clicked position (0-7)
            click_y: Row index of the clicked position (0-7)

        Returns:
            bool: True if the click matches the target coordinate
        """
        if not self.current_coordinate:
            return False

        target_col, target_row = self.current_coordinate
        if not self.is_white_perspective:
            target_col = self._config.GRID_SIZE - 1 - target_col
            target_row = self._config.GRID_SIZE - 1 - target_row

        return (click_x, click_y) == (target_col, target_row)

    def get_coordinate_notation(self, col: int, row: int) -> str:
        """
        Converts board coordinates to algebraic notation.

        Args:
            col: Column index (0-7)
            row: Row index (0-7)

        Returns:
            str: Algebraic notation (e.g., 'A1', 'H8')
        """
        if self.is_white_perspective:
            file = chr(ord('A') + col)
            rank = self._config.GRID_SIZE - row
        else:
            file = chr(ord('A') + (self._config.GRID_SIZE - 1 - col))
            rank = row + 1
        return f"{file}{rank}"


class GamePerformance:
    """
    Manages game performance tracking, scoring, and statistics.
    """

    def __init__(self):
        self._config = GameConfig()
        self.reset_session()
        self.reset_history()

    def reset_session(self) -> None:
        """Resets current session statistics."""
        self.correct_clicks = 0
        self.wrong_clicks = 0
        self.total_response_time = 0.0
        self.fastest_response = float('inf')
        self.slowest_response = 0.0

    def reset_history(self) -> None:
        """Resets historical performance data."""
        self.score_history: List[int] = []
        self.accuracy_history: List[float] = []
        self.correct_clicks_history: List[int] = []
        self.wrong_clicks_history: List[int] = []
        self.avg_time_history: List[float] = []
        self.fastest_time_history: List[float] = []
        self.slowest_time_history: List[float] = []

    def record_attempt(self, is_correct: bool, response_time: float) -> None:
        """
        Records the result of a move attempt.

        Args:
            is_correct: Whether the attempt was successful
            response_time: Time taken to respond in seconds
        """
        if is_correct:
            self.correct_clicks += 1
            self.total_response_time += response_time
            self.fastest_response = min(self.fastest_response, response_time)
            self.slowest_response = max(self.slowest_response, response_time)
        else:
            self.wrong_clicks += 1

    def calculate_score(self) -> int:
        """
        Calculates the current session score based on performance metrics.

        Returns:
            int: Calculated score incorporating accuracy and speed bonuses
        """
        if self.correct_clicks == 0:
            return 0

        base_score = self.correct_clicks * self._config.BASE_SCORE_PER_CORRECT

        accuracy = self.correct_clicks / max(1, (self.correct_clicks + self.wrong_clicks))
        accuracy_bonus = base_score * accuracy

        avg_response_time = self.total_response_time / self.correct_clicks
        speed_bonus = max(0, self._config.SPEED_BONUS_MAX - (avg_response_time * 100))

        penalties = self.wrong_clicks * self._config.PENALTY_PER_WRONG

        return int(base_score + accuracy_bonus + speed_bonus - penalties)

    def get_session_stats(self) -> Dict:
        """
        Returns current session statistics.

        Returns:
            Dict containing session performance metrics
        """
        total_clicks = self.correct_clicks + self.wrong_clicks
        return {
            'score': self.calculate_score(),
            'total_clicks': total_clicks,
            'correct_clicks': self.correct_clicks,
            'wrong_clicks': self.wrong_clicks,
            'accuracy': (self.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0,
            'avg_response_time': (self.total_response_time / self.correct_clicks) if self.correct_clicks > 0 else 0,
            'fastest_response': self.fastest_response if self.fastest_response != float('inf') else 0,
            'slowest_response': self.slowest_response
        }

    def save_session_stats(self) -> None:
        """Records current session statistics in historical data."""
        stats = self.get_session_stats()
        self.score_history.append(stats['score'])
        self.accuracy_history.append(stats['accuracy'])
        self.correct_clicks_history.append(stats['correct_clicks'])
        self.wrong_clicks_history.append(stats['wrong_clicks'])
        self.avg_time_history.append(stats['avg_response_time'])
        self.fastest_time_history.append(stats['fastest_response'])
        self.slowest_time_history.append(stats['slowest_response'])


class GameState:
    """
    Main game state manager that coordinates board state and performance tracking.
    """

    def __init__(self):
        self.board = ChessBoardState()
        self.performance = GamePerformance()
        self.is_active = False
        self.last_coordinate_time: Optional[float] = None

    def start_game(self) -> None:
        """Initializes a new game session."""
        self.is_active = True
        self.performance.reset_session()

    def end_game(self) -> None:
        """Concludes the current game session."""
        self.is_active = False
        self.performance.save_session_stats()
        self.last_coordinate_time = None

    def get_save_data(self) -> Dict:
        """
        Prepares game data for saving.

        Returns:
            Dict containing all historical game data
        """
        return {
            'score_history': self.performance.score_history,
            'accuracy_history': self.performance.accuracy_history,
            'correct_clicks_history': self.performance.correct_clicks_history,
            'wrong_clicks_history': self.performance.wrong_clicks_history,
            'avg_time_history': self.performance.avg_time_history,
            'fastest_time_history': self.performance.fastest_time_history,
            'slowest_time_history': self.performance.slowest_time_history,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def load_save_data(self, data: Dict) -> None:
        """
        Loads saved game data.

        Args:
            data: Dictionary containing saved game statistics
        """
        self.performance.score_history = data['score_history']
        self.performance.accuracy_history = data['accuracy_history']
        self.performance.correct_clicks_history = data['correct_clicks_history']
        self.performance.wrong_clicks_history = data['wrong_clicks_history']
        self.performance.avg_time_history = data['avg_time_history']
        self.performance.fastest_time_history = data['fastest_time_history']
        self.performance.slowest_time_history = data['slowest_time_history']
