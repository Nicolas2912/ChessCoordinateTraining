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
        Sets up the matplotlib figure and axes for visualization with clean, empty subplots.
        """
        self.figure = figure

        # Configure figure to remove extra space around plots
        self.figure.set_facecolor('white')

        # Create GridSpec with appropriate spacing
        gs = figure.add_gridspec(
            2, 2,
            height_ratios=[1, 1],
            width_ratios=[1, 1],
            top=0.9,
            bottom=0.15,
            hspace=0.4,
            wspace=0.3
        )

        # Define titles and labels for each subplot
        plots_config = {
            'score': ('Score History', 'Score'),
            'accuracy': ('Accuracy History', 'Accuracy (%)'),
            'clicks': ('Clicks History', 'Number of Clicks'),
            'time': ('Response Times', 'Time (seconds)')
        }

        # Create and configure subplots
        self.axes = {}
        for idx, (name, (title, ylabel)) in enumerate(plots_config.items()):
            row, col = divmod(idx, 2)
            ax = figure.add_subplot(gs[row, col])
            self.axes[name] = ax

            # Remove all ticks and labels
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])

            # Configure axis labels and title
            ax.set_title(title, pad=15)
            ax.set_xlabel('Games')
            ax.set_ylabel(ylabel)

            # Add very light grid
            ax.grid(True, linestyle='--', alpha=0.5)

            # Show only the frame by making all spines visible and black
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('black')
                spine.set_linewidth(1.0)

            # Set limits to remove the 0.0-1.0 scale
            ax.set_xlim(-0.1, 5)  # Adjust these values as needed
            ax.set_ylim(-0.1, 5)  # Adjust these values as needed

        # Apply tight layout
        self.figure.tight_layout()

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

        x_labels = [f"Game {i + 1}" for i in range(len(self.score_history))]
        x_positions = range(len(x_labels))

        # Clear all subplots
        for ax in self.axes.values():
            ax.clear()

        # Plot score history
        self.axes['score'].plot(x_positions, self.score_history, 'b-o', label='Score')
        for i, score in enumerate(self.score_history):
            self.axes['score'].text(i, score, f'{score}', ha='center', va='bottom')

        # Set appropriate y-axis ticks for score
        min_score = min(self.score_history)
        max_score = max(self.score_history)
        score_range = max_score - min_score
        self.axes['score'].set_ylim(min_score - 0.1 * score_range, max_score + 0.1 * score_range)
        self.axes['score'].set_yticks(self.score_history)
        self.axes['score'].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))

        # Plot accuracy history
        self.axes['accuracy'].plot(x_positions, self.accuracy_history, 'g-o', label='Accuracy')
        for i, acc in enumerate(self.accuracy_history):
            self.axes['accuracy'].text(i, acc, f'{acc:.1f}%', ha='center', va='bottom')

        # Set appropriate y-axis ticks for accuracy
        min_acc = min(self.accuracy_history)
        max_acc = max(self.accuracy_history)
        acc_range = max_acc - min_acc
        self.axes['accuracy'].set_ylim(min_acc - 0.1 * acc_range, max_acc + 0.1 * acc_range)
        self.axes['accuracy'].set_yticks(sorted(set(self.accuracy_history)))
        self.axes['accuracy'].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))

        # Plot clicks history
        self.axes['clicks'].plot(x_positions, self.correct_clicks_history, 'g-o', label='Correct')
        self.axes['clicks'].plot(x_positions, self.wrong_clicks_history, 'r-o', label='Wrong')

        # Set appropriate y-axis ticks for clicks
        all_clicks = self.correct_clicks_history + self.wrong_clicks_history
        min_clicks = min(all_clicks)
        max_clicks = max(all_clicks)
        clicks_range = max_clicks - min_clicks
        self.axes['clicks'].set_ylim(min_clicks - 0.1 * clicks_range, max_clicks + 0.1 * clicks_range)
        self.axes['clicks'].set_yticks(sorted(set(all_clicks)))
        self.axes['clicks'].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))

        # Plot response times
        self.axes['time'].plot(x_positions, self.avg_time_history, 'b-o', label='Average')
        self.axes['time'].plot(x_positions, self.fastest_time_history, 'g-o', label='Fastest')
        self.axes['time'].plot(x_positions, self.slowest_time_history, 'r-o', label='Slowest')

        # Set appropriate y-axis ticks for time
        all_times = (self.avg_time_history + self.fastest_time_history +
                     self.slowest_time_history)
        min_time = min(all_times)
        max_time = max(all_times)
        time_range = max_time - min_time

        # Calculate step size for ticks to avoid overcrowding
        tick_count = 6  # Desired number of ticks
        step = time_range / (tick_count - 1)
        tick_values = [min_time + i * step for i in range(tick_count)]

        # Set y-axis limits with some padding
        self.axes['time'].set_ylim(min_time - 0.1 * time_range,
                                   max_time + 0.1 * time_range)

        # Set custom ticks and format them
        self.axes['time'].set_yticks(tick_values)
        self.axes['time'].yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'{x:.2f}s'))

        # Remove the right and top spines
        self.axes['time'].spines['right'].set_visible(False)
        self.axes['time'].spines['top'].set_visible(False)

        # Add legend
        self.axes['time'].legend()

        # Add grid
        self.axes['time'].grid(True, linestyle='--', alpha=0.7)

        # Common settings for all plots
        for name, ax in self.axes.items():
            # Configure x-axis
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45)

            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)

            # Set labels and title
            ax.set_xlabel('Games')
            title_map = {
                'score': 'Score History',
                'accuracy': 'Accuracy History',
                'clicks': 'Clicks History',
                'time': 'Response Times'
            }
            ax.set_title(title_map[name], pad=15)

        # Add legends where needed
        self.axes['clicks'].legend()
        self.axes['time'].legend()

        # Adjust layout
        plt.tight_layout()

    def _plot_with_style(self, ax, x_positions, x_labels, y_values, style, label):
        """Helper method for consistent plot styling."""
        ax.plot(x_positions, y_values, style, label=label)
        for i, value in enumerate(y_values):
            ax.text(i, value, f'{value:.1f}', ha='center', va='bottom')
        self._configure_axis(ax, x_positions, x_labels)

    def _configure_axis(self, ax, x_positions, x_labels):
        """Helper method for consistent axis configuration."""
        # Set custom x-ticks with game labels
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, rotation=45)

        # Remove y-ticks
        ax.set_yticks([])

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)

        # Set margins for better data visibility
        ax.margins(x=0.1, y=0.2)

    def _setup_axis(self, ax, x_labels, title, ylabel):
        """Helper method to set up consistent axis styling."""
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45)
        ax.set_yticks([])
        ax.set_title(title, pad=15)
        ax.set_xlabel('Games')
        ax.set_ylabel(ylabel)
        ax.grid(True)
        # Remove all spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Only show x-axis labels
        ax.tick_params(axis='y', which='both', length=0)
        ax.margins(x=0.1, y=0.2)

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
