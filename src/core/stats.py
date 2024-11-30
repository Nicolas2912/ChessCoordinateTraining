from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from datetime import datetime
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes


@dataclass
class GameSession:
    """
    Represents a single game session's statistics.
    Tracks performance metrics for one complete game round.
    """
    correct_clicks: int = 0
    wrong_clicks: int = 0
    total_response_time: float = 0.0
    fastest_response: float = float('inf')
    slowest_response: float = 0.0

    def reset(self) -> None:
        """Resets all session statistics to their initial values."""
        self.correct_clicks = 0
        self.wrong_clicks = 0
        self.total_response_time = 0.0
        self.fastest_response = float('inf')
        self.slowest_response = 0.0

    def record_attempt(self, correct: bool, response_time: float) -> None:
        """
        Records a single attempt in the game session.

        Args:
            correct: Whether the attempt was successful
            response_time: Time taken to respond in seconds
        """
        if correct:
            self.correct_clicks += 1
            self.total_response_time += response_time
            self.fastest_response = min(self.fastest_response, response_time)
            self.slowest_response = max(self.slowest_response, response_time)
        else:
            self.wrong_clicks += 1

    def calculate_score(self) -> int:
        """Calculate the final score based on performance metrics."""
        if self.correct_clicks == 0:
            return 0

        # Base score from correct clicks (100 points each)
        base_score = self.correct_clicks * 100

        # Accuracy bonus (up to 100% bonus)
        total_clicks = self.correct_clicks + self.wrong_clicks
        accuracy = self.correct_clicks / total_clicks if total_clicks > 0 else 0
        accuracy_bonus = base_score * accuracy

        # Speed bonus based on average response time
        avg_response_time = self.total_response_time / self.correct_clicks
        speed_bonus = max(0, 500 - (avg_response_time * 100))

        # Penalty for wrong clicks (50 points each)
        penalties = self.wrong_clicks * 50

        return int(base_score + accuracy_bonus + speed_bonus - penalties)

    def get_session_stats(self) -> dict:
        """
        Returns current session statistics.

        Returns:
            Dictionary containing current session metrics including score,
            accuracy, response times, and click counts.
        """
        total_clicks = self.correct_clicks + self.wrong_clicks
        accuracy = (self.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        avg_time = (self.total_response_time / self.correct_clicks) if self.correct_clicks > 0 else 0

        return {
            'score': self.calculate_score(),
            'correct': self.correct_clicks,
            'wrong': self.wrong_clicks,
            'accuracy': accuracy,
            'avg_time': avg_time,
            'fastest_response': self.fastest_response if self.fastest_response != float('inf') else 0,
            'slowest_response': self.slowest_response
        }

    def calculate_accuracy(self) -> float:
        """
        Calculates the current accuracy rate.

        Returns:
            float: Accuracy percentage (0-100)
        """
        total_clicks = self.correct_clicks + self.wrong_clicks
        return (self.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0.0

    def calculate_avg_response_time(self) -> float:
        """
        Calculates the average response time.

        Returns:
            float: Average response time in seconds
        """
        return (self.total_response_time / self.correct_clicks) if self.correct_clicks > 0 else 0.0


class PerformanceTracker:
    """
    Tracks and analyzes long-term performance statistics across multiple game sessions.
    Handles data persistence and visualization of performance trends.
    """

    def __init__(self):
        self.score_history: List[int] = []
        self.accuracy_history: List[float] = []
        self.correct_clicks_history: List[int] = []
        self.wrong_clicks_history: List[int] = []
        self.avg_time_history: List[float] = []
        self.fastest_time_history: List[float] = []
        self.slowest_time_history: List[float] = []
        self.figure: Optional[Figure] = None
        self.axes: Dict[str, Axes] = {}

    def initialize_visualization(self, figure: Figure) -> None:
        """
        Sets up the matplotlib figure and axes for visualization.

        Args:
            figure: Matplotlib figure object for plotting
        """
        self.figure = figure
        self.axes = {
            'score': figure.add_subplot(221),
            'accuracy': figure.add_subplot(222),
            'clicks': figure.add_subplot(223),
            'time': figure.add_subplot(224)
        }

        for ax in self.axes.values():
            ax.tick_params(labelsize=8)
            ax.title.set_fontsize(10)
            ax.xaxis.label.set_fontsize(8)
            ax.yaxis.label.set_fontsize(8)

    def record_session(self, score: int, session: GameSession) -> None:
        """
        Records statistics from a completed game session.

        Args:
            score: Final score for the session
            session: GameSession object containing session statistics
        """
        self.score_history.append(score)
        self.accuracy_history.append(session.calculate_accuracy())
        self.correct_clicks_history.append(session.correct_clicks)
        self.wrong_clicks_history.append(session.wrong_clicks)
        self.avg_time_history.append(session.calculate_avg_response_time())
        self.fastest_time_history.append(
            session.fastest_response if session.fastest_response != float('inf') else 0.0
        )
        self.slowest_time_history.append(session.slowest_response)

    def update_visualizations(self):
        """Updates all performance visualization graphs with current data."""
        if not self.score_history:
            return

        # Generate x-axis labels
        x_labels = [f"Game {i + 1}" for i in range(len(self.score_history))]

        # Clear all plots
        for ax in self.axes.values():
            ax.clear()

        # Plot score history
        self.axes['score'].plot(x_labels, self.score_history, 'b-o', label='Score')
        for i, score in enumerate(self.score_history):
            self.axes['score'].text(i, score, f'{score}', ha='center', va='bottom')
        self.axes['score'].set_title('Score History')
        self.axes['score'].set_xlabel('Games')
        self.axes['score'].set_ylabel('Score')
        self.axes['score'].tick_params(axis='x', rotation=45)
        self.axes['score'].grid(True, linestyle='--', alpha=0.7)

        # Plot accuracy history
        self.axes['accuracy'].plot(x_labels, self.accuracy_history, 'g-o', label='Accuracy')
        for i, acc in enumerate(self.accuracy_history):
            self.axes['accuracy'].text(i, acc, f'{acc:.1f}%', ha='center', va='bottom')
        self.axes['accuracy'].set_title('Accuracy History')
        self.axes['accuracy'].set_xlabel('Games')
        self.axes['accuracy'].set_ylabel('Accuracy (%)')
        self.axes['accuracy'].tick_params(axis='x', rotation=45)
        self.axes['accuracy'].grid(True, linestyle='--', alpha=0.7)

        # Plot clicks history
        self.axes['clicks'].plot(x_labels, self.correct_clicks_history, 'g-o', label='Correct')
        self.axes['clicks'].plot(x_labels, self.wrong_clicks_history, 'r-o', label='Wrong')
        self.axes['clicks'].set_title('Clicks History')
        self.axes['clicks'].set_xlabel('Games')
        self.axes['clicks'].set_ylabel('Number of Clicks')
        self.axes['clicks'].legend()
        self.axes['clicks'].tick_params(axis='x', rotation=45)
        self.axes['clicks'].grid(True, linestyle='--', alpha=0.7)

        # Plot response times
        self.axes['time'].plot(x_labels, self.avg_time_history, 'b-o', label='Average')
        self.axes['time'].plot(x_labels, self.fastest_time_history, 'g-o', label='Fastest')
        self.axes['time'].plot(x_labels, self.slowest_time_history, 'r-o', label='Slowest')
        self.axes['time'].set_title('Response Times')
        self.axes['time'].set_xlabel('Games')
        self.axes['time'].set_ylabel('Time (seconds)')
        self.axes['time'].legend()
        self.axes['time'].tick_params(axis='x', rotation=45)
        self.axes['time'].grid(True, linestyle='--', alpha=0.7)

        # Adjust layout to prevent overlapping
        self.figure.tight_layout()

    def _plot_score_history(self, x_labels: List[str]) -> None:
        """Plots score history graph."""
        self.axes['score'].plot(x_labels, self.score_history, 'b-o', label='Score')
        for i, score in enumerate(self.score_history):
            self.axes['score'].text(i, score, f'{score}', ha='center', va='bottom')
        self.axes['score'].set_title('Score History')
        self.axes['score'].set_xlabel('Games')
        self.axes['score'].set_ylabel('Score')

    def _plot_accuracy_history(self, x_labels: List[str]) -> None:
        """Plots accuracy history graph."""
        self.axes['accuracy'].plot(x_labels, self.accuracy_history, 'g-o', label='Accuracy')
        for i, acc in enumerate(self.accuracy_history):
            self.axes['accuracy'].text(i, acc, f'{acc:.1f}%', ha='center', va='bottom')
        self.axes['accuracy'].set_title('Accuracy History')
        self.axes['accuracy'].set_xlabel('Games')
        self.axes['accuracy'].set_ylabel('Accuracy (%)')

    def _plot_clicks_history(self, x_labels: List[str]) -> None:
        """Plots clicks history graph."""
        self.axes['clicks'].plot(x_labels, self.correct_clicks_history, 'g-o', label='Correct')
        self.axes['clicks'].plot(x_labels, self.wrong_clicks_history, 'r-o', label='Wrong')
        self.axes['clicks'].set_title('Clicks History')
        self.axes['clicks'].set_xlabel('Games')
        self.axes['clicks'].set_ylabel('Number of Clicks')
        self.axes['clicks'].legend()

    def _plot_response_times(self, x_labels: List[str]) -> None:
        """Plots response times graph."""
        self.axes['time'].plot(x_labels, self.avg_time_history, 'b-o', label='Average')
        self.axes['time'].plot(x_labels, self.fastest_time_history, 'g-o', label='Fastest')
        self.axes['time'].plot(x_labels, self.slowest_time_history, 'r-o', label='Slowest')
        self.axes['time'].set_title('Response Times')
        self.axes['time'].set_xlabel('Games')
        self.axes['time'].set_ylabel('Time (seconds)')
        self.axes['time'].legend()

    def save_statistics(self, filepath: str) -> None:
        """
        Saves current statistics to a JSON file.

        Args:
            filepath: Path where the statistics file should be saved

        Raises:
            IOError: If there is an error writing to the file
        """
        stats_data = {
            'score_history': self.score_history,
            'accuracy_history': self.accuracy_history,
            'correct_clicks_history': self.correct_clicks_history,
            'wrong_clicks_history': self.wrong_clicks_history,
            'avg_time_history': self.avg_time_history,
            'fastest_time_history': self.fastest_time_history,
            'slowest_time_history': self.slowest_time_history,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(filepath, 'w') as f:
            json.dump(stats_data, f, indent=4)

    def load_statistics(self, filepath: str) -> None:
        """
        Loads statistics from a JSON file.

        Args:
            filepath: Path to the statistics file to load

        Raises:
            IOError: If there is an error reading the file
            ValueError: If the file format is invalid
        """
        try:
            with open(filepath, 'r') as f:
                stats_data = json.load(f)

            # Load all statistics histories
            self.score_history = stats_data['score_history']
            self.accuracy_history = stats_data['accuracy_history']
            self.correct_clicks_history = stats_data['correct_clicks_history']
            self.wrong_clicks_history = stats_data['wrong_clicks_history']
            self.avg_time_history = stats_data['avg_time_history']
            self.fastest_time_history = stats_data['fastest_time_history']
            self.slowest_time_history = stats_data['slowest_time_history']

            # Store the timestamp if available
            self.last_loaded_timestamp = stats_data.get('timestamp', None)

        except KeyError as e:
            raise ValueError(f"Invalid statistics file format: missing {e}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file format")

    def get_last_timestamp(self) -> str:
        """
        Returns the timestamp of the last loaded statistics file.

        Returns:
            str: Timestamp string or None if not available
        """
        return getattr(self, 'last_loaded_timestamp', None)

    def has_data(self) -> bool:
        """
        Checks if there are any statistics to save.

        Returns:
            bool: True if there are statistics to save, False otherwise
        """
        return bool(self.score_history)
