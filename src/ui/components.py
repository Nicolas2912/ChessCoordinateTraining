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
        'error': '#dc2626',  # Red for critical actions
        'success': '#22c55e'  # Green for success/start actions

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
        self.parent = parent

        # Initialize canvas with minimum size
        self.canvas = tk.Canvas(
            parent,
            bg=self.config.COLORS['background'],
            highlightthickness=0,
            width=600,  # Initial minimum width
            height=600  # Initial minimum height
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Initialize dimensions
        self.update_dimensions()

        # Draw initial board
        self.draw_board(True)

        # Bind resize event
        self.canvas.bind('<Configure>', self._on_resize)

    def update_dimensions(self):
        """
        Updates board dimensions based on current window size while ensuring proper scaling
        and maintaining aspect ratio.
        """
        # Get current canvas size
        canvas_width = self.canvas.winfo_width() or 600
        canvas_height = self.canvas.winfo_height() or 600

        # Calculate available space for the board
        # Leave some padding for the rank/file labels and margins
        padding = 80  # Space for labels and margins
        available_space = min(canvas_width, canvas_height) - padding

        # Calculate tile size based on available space
        # Ensure minimum size of 30px and allow growth based on window size
        self.config.TILE_SIZE = max(30, available_space // (self.config.GRID_SIZE + 1))

        # Calculate board dimensions
        self.board_width = self.config.TILE_SIZE * self.config.GRID_SIZE
        self.board_height = self.board_width

        # Calculate total dimensions including space for labels
        self.total_width = self.board_width + (2 * self.config.TILE_SIZE)
        self.total_height = self.board_height + (2 * self.config.TILE_SIZE)

    def _on_resize(self, event):
        """
        Handles window resize events with debouncing to prevent excessive redraws.
        """
        # Ensure minimum window size
        if event.width > 100 and event.height > 100:
            # Cancel previous timer if it exists
            if hasattr(self, '_resize_timer'):
                self.canvas.after_cancel(self._resize_timer)

            # Set new timer for delayed resize
            self._resize_timer = self.canvas.after(100, self._perform_resize)

    def _perform_resize(self):
        """
        Actually performs the resize operation and updates the board.
        """
        self.update_dimensions()
        self.draw_board(True)  # Maintain current perspective

        # Update coordinates if they were visible
        if self.coordinates_visible:
            self.toggle_coordinates(True)
            self.toggle_coordinates(True)

    def _resize_board(self, event):
        """Actually perform the board resize."""
        if not event:
            return

        # Get available space
        available_width = event.width - 40
        available_height = event.height - 40

        # Calculate new tile size
        new_tile_size = min(available_width, available_height) // (self.config.GRID_SIZE + 2)

        # Only redraw if size changed significantly (at least 5 pixels)
        if abs(new_tile_size - self.config.TILE_SIZE) >= 5:
            self.config.TILE_SIZE = new_tile_size
            self.board_width = self.config.TILE_SIZE * self.config.GRID_SIZE
            self.total_height = self.board_width
            self.canvas_padding = self.config.TILE_SIZE
            self.canvas_width = self.board_width + (2 * self.canvas_padding)
            self.canvas_height = self.total_height + (2 * self.canvas_padding)

            # Update canvas size and redraw
            self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
            self.draw_board(True)

    def draw_board(self, is_white_perspective: bool) -> None:
        """Draws the chessboard with current perspective."""
        was_coordinates_visible = self.coordinates_visible
        self.canvas.delete("all")

        # Calculate board position to center it in canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = (canvas_width - self.board_width) // 2
        offset_y = (canvas_height - self.board_height) // 2

        # Draw board background
        self.canvas.create_rectangle(
            offset_x, offset_y,
            offset_x + self.board_width,
            offset_y + self.board_height,
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

                x1 = offset_x + col * self.config.TILE_SIZE
                y1 = offset_y + row * self.config.TILE_SIZE
                x2 = x1 + self.config.TILE_SIZE
                y2 = y1 + self.config.TILE_SIZE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="",
                    width=0
                )

        # Restore coordinates if they were visible
        if was_coordinates_visible:
            self.coordinates_visible = False
            self.coordinates_text.clear()
            self.toggle_coordinates(is_white_perspective)

    def bind_click(self, callback):
        """Bind click event to canvas."""
        self.canvas.bind("<Button-1>", self._handle_click(callback))

    def _handle_click(self, callback):
        """
        Creates a click handler that accurately translates mouse coordinates to board positions,
        accounting for dynamic board sizing.
        """

        def handler(event):
            # Get current canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Calculate current board position (centered in canvas)
            offset_x = (canvas_width - self.board_width) // 2
            offset_y = (canvas_height - self.board_height) // 2

            # Calculate relative position within the board
            board_x = event.x - offset_x
            board_y = event.y - offset_y

            # Check if click is within board bounds
            if (0 <= board_x <= self.board_width and
                    0 <= board_y <= self.board_height):

                # Calculate tile indices based on current tile size
                tile_x = int(board_x // self.config.TILE_SIZE)
                tile_y = int(board_y // self.config.TILE_SIZE)

                # Verify tile coordinates are within bounds
                if (0 <= tile_x < self.config.GRID_SIZE and
                        0 <= tile_y < self.config.GRID_SIZE):
                    # Create new event with tile coordinates
                    new_event = type('Event', (), {})()
                    new_event.x = tile_x
                    new_event.y = tile_y
                    callback(new_event)

        return handler

    def toggle_coordinates(self, is_white_perspective: bool) -> None:
        """
        Toggles coordinate display with proper scaling and positioning.
        """
        if self.coordinates_visible:
            for text_id in self.coordinates_text.values():
                self.canvas.delete(text_id)
            self.coordinates_text.clear()
        else:
            # Calculate board position
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            offset_x = (canvas_width - self.board_width) // 2
            offset_y = (canvas_height - self.board_height) // 2

            # Scale font size with tile size
            font_size = max(10, min(18, self.config.TILE_SIZE // 3))

            for row in range(self.config.GRID_SIZE):
                for col in range(self.config.GRID_SIZE):
                    actual_row = row if is_white_perspective else (self.config.GRID_SIZE - 1 - row)
                    actual_col = col if is_white_perspective else (self.config.GRID_SIZE - 1 - col)

                    # Calculate center of tile
                    x = offset_x + (col + 0.5) * self.config.TILE_SIZE
                    y = offset_y + (row + 0.5) * self.config.TILE_SIZE

                    # Generate coordinate text
                    file_letter = chr(ord('A') + actual_col)
                    rank_number = str(self.config.GRID_SIZE - actual_row)
                    coord_text = f"{file_letter}{rank_number}"

                    # Set text color based on square color
                    text_color = "white" if ((actual_row + actual_col) % 2 == 1) else "black"

                    # Create centered text with scaled font size
                    text_id = self.canvas.create_text(
                        x, y,
                        text=coord_text,
                        font=("Arial", font_size),
                        fill=text_color,
                        anchor="center"
                    )
                    self.coordinates_text[(col, row)] = text_id

        self.coordinates_visible = not self.coordinates_visible

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

    def check_coordinate(self, event):
        """Convert click coordinates to board position."""
        # Calculate board offset
        offset_x = (self.canvas.winfo_width() - self.board_width) // 2
        offset_y = (self.canvas.winfo_height() - self.total_height) // 2

        # Adjust click coordinates based on offset
        adjusted_x = event.x - offset_x
        adjusted_y = event.y - offset_y

        # Check if click is within board bounds
        if (0 <= adjusted_x <= self.board_width and
                0 <= adjusted_y <= self.total_height):
            return adjusted_x // self.config.TILE_SIZE, adjusted_y // self.config.TILE_SIZE
        return None


class CoordinateDisplay:
    """Display widget for showing the current target coordinate."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.frame = tk.Frame(
            parent,
            bg=config.COLORS['background'],
            highlightbackground=config.COLORS['secondary'],
            highlightthickness=1,
            relief="ridge",
            bd=0
        )

        # Configure frame to expand horizontally
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(
            self.frame,
            text="Click Start to begin",
            font=config.FONTS['coordinate'],
            fg=config.COLORS['accent'],
            bg=config.COLORS['background']
        )
        self.label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def update_text(self, text: str) -> None:
        """Updates the displayed coordinate text."""
        self.label.config(text=text)


class StatisticsPanel:
    """Panel for displaying current game statistics."""

    def __init__(self, parent: tk.Widget, config: UIConfig):
        self.frame = tk.Frame(parent, bg=config.COLORS['background'])

        # Configure grid columns
        for i in range(4):  # For the four statistics
            self.frame.grid_columnconfigure(i, weight=1)

        # Initialize the statistics labels dictionary
        self.stat_labels = {}

        # Create and store labels with consistent keys
        labels_config = [
            ("correct", "Correct: 0"),
            ("wrong", "Wrong: 0"),
            ("accuracy", "Accuracy: 0%"),
            ("avg_time", "Avg Time: 0.0s")
        ]

        for col, (key, text) in enumerate(labels_config):
            self._create_label(config, key, text, col)

        # Create score label
        self.score_label = tk.Label(
            self.frame,
            text="Score: 0",
            font=config.FONTS['header'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        self.score_label.grid(row=1, column=0, columnspan=4, pady=5)

    def _create_label(self, config: UIConfig, key: str, initial_text: str, col: int):
        """Helper method to create and store a statistics label."""
        label = tk.Label(
            self.frame,
            text=initial_text,
            font=config.FONTS['normal'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        label.grid(row=0, column=col, padx=5)
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
        self.frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Timer controls frame
        self.timer_frame = tk.Frame(self.frame, bg=config.COLORS['background'])
        self.timer_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Configure grid columns for timer frame
        self.timer_frame.grid_columnconfigure(1, weight=1)  # Give weight to label column

        # Initialize duration variable and create slider
        self.duration_var = tk.IntVar(value=30)
        self.duration_slider = ttk.Scale(
            self.timer_frame,
            from_=5,
            to=60,
            orient='horizontal',
            length=150,
            variable=self.duration_var,
            command=self._on_slider_change
        )
        self.duration_slider.grid(row=0, column=0, padx=(0, 5))

        # Timer display label
        self.timer_label = tk.Label(
            self.timer_frame,
            text="Time: 30s",
            font=config.FONTS['subheader'],
            fg=config.COLORS['primary'],
            bg=config.COLORS['background']
        )
        self.timer_label.grid(row=0, column=1, sticky="w")

        # Button frame
        self.button_frame = tk.Frame(self.frame, bg=config.COLORS['background'])
        self.button_frame.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Equal weight for all buttons


    def create_buttons(self, commands: dict, config: UIConfig) -> None:
        """Creates and configures control buttons with specified commands."""
        button_configs = [
            {"text": "Start", "command": commands.get('start'), "color": config.COLORS['success']},
            {"text": "Flip Board", "command": commands.get('flip'), "color": config.COLORS['accent']},
            {"text": "Show Coordinates", "command": commands.get('toggle_coords'), "color": config.COLORS['accent']},
            {"text": "Save Stats", "command": commands.get('save'), "color": config.COLORS['accent']},
            {"text": "Load Stats", "command": commands.get('load'), "color": config.COLORS['accent']},
            {"text": "Exit", "command": commands.get('exit'), "color": config.COLORS['error']}
        ]

        # Clear existing buttons if any
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Create new buttons
        for i, btn_config in enumerate(button_configs):
            if btn_config["command"] is not None:
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
                button.grid(row=0, column=i, padx=2, sticky="ew")

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
        # Create a frame to hold the canvas
        self.frame = tk.Frame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Create figure with tight layout
        self.fig = plt.figure(constrained_layout=True)

        # Create GridSpec for better subplot management
        self.gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Create subplots
        self.axes = {
            'score': self.fig.add_subplot(self.gs[0, 0]),
            'accuracy': self.fig.add_subplot(self.gs[0, 1]),
            'clicks': self.fig.add_subplot(self.gs[1, 0]),
            'time': self.fig.add_subplot(self.gs[1, 1])
        }

        # Style configuration
        for ax in self.axes.values():
            ax.tick_params(labelsize=8)
            ax.title.set_fontsize(10)
            ax.xaxis.label.set_fontsize(8)
            ax.yaxis.label.set_fontsize(8)

        # Create canvas with dynamic sizing
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # Bind resize event
        self.frame.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """Handle window resize events."""
        # Update figure size based on frame size
        w, h = event.width / 100, event.height / 100  # Convert to inches
        if w > 0 and h > 0:  # Prevent invalid figure sizes
            self.fig.set_size_inches(w, h)
            self.refresh()

    def get_figure(self) -> Figure:
        """Returns the matplotlib figure object."""
        return self.fig

    def refresh(self) -> None:
        """Refreshes the graph display."""
        self.canvas.draw()
