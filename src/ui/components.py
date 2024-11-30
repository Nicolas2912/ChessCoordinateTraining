import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


@dataclass
class UIConfig:
    """Configuration settings for UI components."""
    COLORS = {
        'primary': '#1a365d',  # Dark blue
        'secondary': '#2d3748',  # Dark gray
        'white_square': '#f7fafc',  # Light gray-white
        'black_square': '#4a5568',  # Medium gray
        'accent': '#3182ce',  # Bright blue
        'text': '#2d3748',  # Dark gray
        'background': '#ffffff',  # White
        'error': '#dc2626'  # Red for critical actions
    }
    FONTS = {
        'header': ('Helvetica', 14, 'bold'),
        'subheader': ('Helvetica', 12, 'bold'),
        'normal': ('Helvetica', 10),
        'coordinate': ('Helvetica', 24, 'bold')
    }
    GRID_SIZE: int = 8
    TILE_SIZE: int = 60


class ChessboardCanvas:
    """Canvas widget for rendering the interactive chessboard."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.config = config
        self.coordinates_visible = False
        self.coordinates_text = {}

        # Calculate the exact width needed for the board
        self.board_width = self.config.GRID_SIZE * self.config.TILE_SIZE
        # Add small padding for file letters below the board
        self.total_height = self.board_width + 40

        # Create canvas with exact dimensions
        self.canvas = tk.Canvas(
            parent,
            width=self.board_width,  # Exact width for 8x8 grid
            height=self.total_height,  # Height plus space for file letters
            bg=self.config.COLORS['background']
        )
        self.canvas.pack(pady=10)

    def draw_board(self, is_white_perspective: bool) -> None:
        """Draws the chessboard with current perspective."""
        was_coordinates_visible = self.coordinates_visible
        self.canvas.delete("all")

        # Draw the outer border
        self.canvas.create_rectangle(
            0, 0,
            self.board_width, self.board_width,
            fill=self.config.COLORS['background'],
            width=2,
            outline=self.config.COLORS['secondary']
        )

        # Draw squares
        for row in range(self.config.GRID_SIZE):
            for col in range(self.config.GRID_SIZE):
                actual_row = row if is_white_perspective else (self.config.GRID_SIZE - 1 - row)
                actual_col = col if is_white_perspective else (self.config.GRID_SIZE - 1 - col)

                color = self.config.COLORS['white_square'] if (actual_row + actual_col) % 2 == 0 \
                    else self.config.COLORS['black_square']

                x1 = col * self.config.TILE_SIZE
                y1 = row * self.config.TILE_SIZE
                x2 = (col + 1) * self.config.TILE_SIZE
                y2 = (row + 1) * self.config.TILE_SIZE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="",
                    width=0
                )

        # Restore coordinates if they were visible
        if was_coordinates_visible:
            self.coordinates_text.clear()
            self.coordinates_visible = False
            self.toggle_coordinates(is_white_perspective)

    def bind_click(self, callback: Callable) -> None:
        """Binds click event to the canvas."""
        self.canvas.bind("<Button-1>", callback)

    def toggle_coordinates(self, is_white_perspective: bool = True) -> None:
        """Toggles the visibility of coordinate labels on the chess board."""
        print("Toggling coordinates")  # Debug print

        if self.coordinates_visible:
            # Hide coordinates
            for text_id in self.coordinates_text.values():
                self.canvas.delete(text_id)
            self.coordinates_text.clear()
        else:
            # Show coordinates
            for row in range(self.config.GRID_SIZE):
                for col in range(self.config.GRID_SIZE):
                    # Calculate position
                    x = col * self.config.TILE_SIZE + self.config.TILE_SIZE / 2
                    y = row * self.config.TILE_SIZE + self.config.TILE_SIZE / 2

                    # Get coordinate text
                    coord_text = self.get_coordinate_text(col, row, is_white_perspective)

                    # Determine text color based on square color
                    text_color = "white" if (row + col) % 2 == 1 else "black"

                    # Create text on canvas
                    text_id = self.canvas.create_text(
                        x, y,
                        text=coord_text,
                        font=("Arial", 12),
                        fill=text_color
                    )
                    self.coordinates_text[(col, row)] = text_id

        # Toggle visibility flag
        self.coordinates_visible = not self.coordinates_visible
        print(f"Coordinates visible: {self.coordinates_visible}")  # Debug print

    def get_coordinate_text(self, col: int, row: int, is_white_perspective: bool = True) -> str:
        """
        Generates algebraic notation for a given board position.

        Args:
            col: Column index (0-7)
            row: Row index (0-7)
            is_white_perspective: Whether the board is viewed from white's perspective

        Returns:
            str: Algebraic notation (e.g., 'A1', 'H8')
        """
        if is_white_perspective:
            file = chr(ord('A') + col)
            rank = self.config.GRID_SIZE - row
        else:
            file = chr(ord('A') + (self.config.GRID_SIZE - 1 - col))
            rank = row + 1
        return f"{file}{rank}"


class CoordinateDisplay:
    """Display widget for showing the current target coordinate."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.frame = tk.Frame(
            parent,
            width=config.GRID_SIZE * config.TILE_SIZE + 100,
            height=40,
            bg=config.COLORS['background'],
            highlightbackground=config.COLORS['secondary'],
            highlightthickness=1,
            relief="ridge",
            bd=0
        )
        self.frame.pack(pady=10)
        self.frame.pack_propagate(False)

        self.label = tk.Label(
            self.frame,
            text="Click Start to begin",
            font=config.FONTS['coordinate'],
            fg=config.COLORS['accent'],
            bg=config.COLORS['background']
        )
        self.label.pack(expand=True, fill="both")

    def update_text(self, text: str) -> None:
        """Updates the displayed coordinate text."""
        self.label.config(text=text)


class StatisticsPanel:
    """Panel for displaying current game statistics."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.frame = tk.Frame(parent, bg=config.COLORS['background'])
        self.frame.pack(pady=10)

        # Initialize the statistics labels dictionary
        self.stat_labels = {}

        # Create and store labels with consistent keys
        self._create_label(config, "correct", "Correct: 0")
        self._create_label(config, "wrong", "Wrong: 0")
        self._create_label(config, "accuracy", "Accuracy: 0%")
        self._create_label(config, "avg_time", "Avg Time: 0.0s")

        # Create score label separately as it has different styling
        self.score_label = tk.Label(
            parent,
            text="Score: 0",
            font=config.FONTS['header'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        self.score_label.pack(pady=5)

    def _create_label(self, config: UIConfig, key: str, initial_text: str):
        """Helper method to create and store a statistics label."""
        label = tk.Label(
            self.frame,
            text=initial_text,
            font=config.FONTS['normal'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        label.pack(side="left", padx=5)
        self.stat_labels[key] = label

    def update_stats(self, stats: dict) -> None:
        """Updates all statistics displays with current values."""
        self.stat_labels["correct"].config(text=f"Correct: {stats['correct']}")
        self.stat_labels["wrong"].config(text=f"Wrong: {stats['wrong']}")
        self.stat_labels["accuracy"].config(text=f"Accuracy: {stats['accuracy']:.1f}%")
        self.stat_labels["avg_time"].config(text=f"Avg Time: {stats['avg_time']:.2f}s")
        self.score_label.config(text=f"Score: {stats['score']}")


class GameControls:
    """Control panel for game settings and actions."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.frame = tk.Frame(parent, bg=config.COLORS['background'])
        self.frame.pack(side="bottom", pady=10)

        # Timer controls frame
        self.timer_frame = tk.Frame(self.frame, bg=config.COLORS['background'])
        self.timer_frame.pack(pady=5)

        # Initialize duration variable and create slider
        self.duration_var = tk.IntVar(value=30)
        self.duration_slider = ttk.Scale(
            self.timer_frame,
            from_=5,
            to=60,
            orient='horizontal',
            length=150,
            variable=self.duration_var,
            command=self._on_slider_change  # Add callback for slider movement
        )
        self.duration_slider.pack(side='left', padx=5)

        # Timer display label
        self.timer_label = tk.Label(
            self.timer_frame,
            text="Time: 30s",  # Initial value
            font=config.FONTS['subheader'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        self.timer_label.pack(side='left', padx=5)

        # Button frame
        self.button_frame = tk.Frame(self.frame, bg=config.COLORS['background'])
        self.button_frame.pack(pady=5)

    def create_buttons(self, commands: dict, config: UIConfig) -> None:
        """Creates and configures control buttons with specified commands."""
        button_configs = [
            {"text": "Start", "command": commands.get('start'), "color": config.COLORS['accent']},
            {"text": "Flip Board", "command": commands.get('flip'), "color": config.COLORS['accent']},
            {"text": "Show Coordinates", "command": commands.get('toggle_coords'),
             "color": config.COLORS['accent']},
            {"text": "Save Stats", "command": commands.get('save'), "color": config.COLORS['accent']},
            {"text": "Load Stats", "command": commands.get('load'), "color": config.COLORS['accent']},
            {"text": "Exit", "command": commands.get('exit'), "color": config.COLORS['error']}
        ]

        # Clear existing buttons if any
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Create new buttons
        for btn_config in button_configs:
            if btn_config["command"] is not None:  # Only create button if command exists
                button = tk.Button(
                    self.button_frame,
                    text=btn_config["text"],
                    command=btn_config["command"],
                    font=config.FONTS['normal'],
                    bg=btn_config["color"],
                    fg='white',
                    relief="flat",
                    padx=15,
                    pady=5,
                    cursor="hand2"
                )
                button.pack(side="left", padx=2)

    def update_timer(self, time_left: int) -> None:
        """
        Updates the timer display during gameplay.

        Args:
            time_left: Remaining time in seconds
        """
        self.timer_label.config(text=f"Time Left: {time_left}s")

    def get_duration(self) -> int:
        """
        Returns the current slider value.

        Returns:
            int: Selected duration in seconds
        """
        return self.duration_var.get()

    def _on_slider_change(self, value):
        """
        Updates the timer label when the slider value changes.

        Args:
            value: Current slider value (passed automatically by the slider widget)
        """
        # Convert string value to integer and update label
        duration = int(float(value))
        self.timer_label.config(text=f"Time: {duration}s")


class PerformanceGraphs:
    """Matplotlib-based performance visualization panel."""

    def __init__(self, parent: tk.Widget):
        self.fig = plt.figure(figsize=(8, 6))
        plt.subplots_adjust(hspace=0.5, wspace=0.3)

        # Create subplots
        self.axes = {
            'score': self.fig.add_subplot(221),
            'accuracy': self.fig.add_subplot(222),
            'clicks': self.fig.add_subplot(223),
            'time': self.fig.add_subplot(224)
        }

        # Style configuration
        for ax in self.axes.values():
            ax.tick_params(labelsize=8)
            ax.title.set_fontsize(10)
            ax.xaxis.label.set_fontsize(8)
            ax.yaxis.label.set_fontsize(8)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True)

    def get_figure(self) -> Figure:
        """Returns the matplotlib figure object."""
        return self.fig

    def refresh(self) -> None:
        """Refreshes the graph display."""
        self.canvas.draw()
