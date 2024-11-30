import tkinter as tk
import time
from ChessCoordinateTraining.src.core.game_logic import GameState, GameConfig
from ChessCoordinateTraining.src.core.stats import GameSession, PerformanceTracker
from ChessCoordinateTraining.src.ui.components import (
    UIConfig,
    ChessboardCanvas,
    CoordinateDisplay,
    StatisticsPanel,
    GameControls,
    PerformanceGraphs
)


class ChessTrainer:
    """
    Main application class that orchestrates the chess coordinates training system.
    Integrates game logic, statistics tracking, and UI components.
    """

    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Chess Coordinates Trainer")

        # Initialize configurations
        self.game_config = GameConfig()
        self.ui_config = UIConfig()

        # Initialize core components
        self.game_state = GameState()
        self.game_session = GameSession()
        self.performance_tracker = PerformanceTracker()

        # Setup UI layout
        self.setup_window_layout()
        self.initialize_components()
        self.bind_events()

    def setup_window_layout(self):
        """Creates the main frame structure for the application."""
        self.root.configure(bg=self.ui_config.COLORS['background'])
        self.root.option_add('*Font', 'Helvetica 10')

        # Create main frames
        self.game_frame = tk.Frame(self.root, bg=self.ui_config.COLORS['background'])
        self.game_frame.pack(side="left", padx=10, fill="both", expand=True)

        self.right_frame = tk.Frame(self.root, bg=self.ui_config.COLORS['background'])
        self.right_frame.pack(side="right", padx=20, fill="both", expand=True)

        # Add countdown display frame
        self.countdown_frame = tk.Frame(
            self.game_frame,
            bg=self.ui_config.COLORS['background'],
            height=60  # Fixed height for consistent spacing
        )
        self.countdown_frame.pack(fill='x', pady=10)

        # Create large countdown label
        self.countdown_label = tk.Label(
            self.countdown_frame,
            text="",
            font=("Helvetica", 48, "bold"),  # Large, bold font
            fg=self.ui_config.COLORS['accent'],
            bg=self.ui_config.COLORS['background']
        )
        self.countdown_label.pack(expand=True)

    def initialize_components(self):
        """Initializes and configures all UI components."""
        # Create perspective label
        self.perspective_label = tk.Label(
            self.game_frame,
            text="View: White's perspective",
            font=self.ui_config.FONTS['header'],
            fg=self.ui_config.COLORS['primary'],
            bg=self.ui_config.COLORS['background']
        )
        self.perspective_label.pack(pady=5)

        # Initialize game board
        self.chessboard = ChessboardCanvas(self.game_frame, self.ui_config)
        self.coordinate_display = CoordinateDisplay(self.game_frame, self.ui_config)

        # Draw initial board
        self.chessboard.draw_board(self.game_state.board.is_white_perspective)

        # Initialize statistics and controls
        self.stats_panel = StatisticsPanel(self.right_frame, self.ui_config)
        self.performance_graphs = PerformanceGraphs(self.right_frame)
        self.game_controls = GameControls(self.right_frame, self.ui_config)

        # Configure performance tracker with matplotlib figure
        self.performance_tracker.initialize_visualization(self.performance_graphs.get_figure())

        # Setup control buttons with commands
        self.game_controls.create_buttons({
            'start': self.start_game,
            'flip': self.flip_board,
            'toggle_coords': self.toggle_coordinates,
            'save': self.save_statistics,
            'load': self.load_statistics,
            'exit': self.exit_application
        }, self.ui_config)

    def bind_events(self):
        """Sets up event bindings for user interactions."""
        self.chessboard.bind_click(self.handle_board_click)

    def start_game(self):
        """Initiates a new game session."""
        self.duration = self.game_controls.get_duration()
        self.game_state.start_game()
        self.game_session.reset()

        # Update UI for game start
        coordinate, col, row = self.game_state.board.generate_coordinate()
        self.coordinate_display.update_text(coordinate)

        # Initialize timing variables
        self.time_left = self.duration
        self.last_coordinate_time = time.time()

        # Update countdown display
        self.countdown_label.config(
            text=str(self.time_left),
            fg=self.ui_config.COLORS['accent']  # Start with normal color
        )

        # Start timer
        self.update_timer()

    def update_timer(self):
        """Updates the game timer and manages game state based on time."""
        if self.time_left > 0 and self.game_state.is_active:
            # Update both the control timer and the large countdown
            self.game_controls.update_timer(self.time_left)

            # Update countdown display with color coding
            if self.time_left <= 5:
                color = '#dc2626'  # Red for last 5 seconds
            elif self.time_left <= 10:
                color = '#f59e0b'  # Orange for last 10 seconds
            else:
                color = self.ui_config.COLORS['accent']  # Normal color

            self.countdown_label.config(
                text=str(self.time_left),
                fg=color
            )

            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.countdown_label.config(text="Time's Up!")
            self.end_game()

    def end_game(self):
        """
        Handles the end of a game session and updates performance statistics.
        """
        self.game_state.is_active = False
        self.coordinate_display.update_text("Game Over!")
        self.game_controls.update_timer(0)

        # Calculate final statistics
        final_stats = self.game_session.get_session_stats()

        # Update performance tracker with session results
        self.performance_tracker.record_session(
            final_stats['score'],
            self.game_session
        )

        # Update statistics panel with final stats
        self.stats_panel.update_stats(final_stats)

        # Update and display performance graphs
        self.performance_tracker.update_visualizations()
        self.performance_graphs.refresh()

    def handle_board_click(self, event):
        """Processes user clicks on the chessboard."""
        if not self.game_state.is_active:
            return

        if self.game_state.board.validate_click(event.x, event.y):
            self.record_correct_click()
        else:
            self.record_wrong_click()

        self.update_display()

    def record_correct_click(self):
        """Handles a correct square click."""
        # Record the successful attempt
        response_time = time.time() - self.last_coordinate_time
        self.game_session.record_attempt(True, response_time)

        # Generate new coordinate
        coordinate, col, row = self.game_state.board.generate_coordinate()
        self.coordinate_display.update_text(coordinate)
        self.last_coordinate_time = time.time()

    def record_wrong_click(self):
        """Handles an incorrect square click."""
        # Record the failed attempt
        self.game_session.record_attempt(False, 0)

    def update_display(self):
        """Updates all UI elements with current game state."""
        stats = self.game_session.get_session_stats()
        self.stats_panel.update_stats(stats)
        self.performance_tracker.update_visualizations()

    def flip_board(self):
        """Toggles the board perspective."""
        self.game_state.board.flip_perspective()
        self.perspective_label.config(
            text=f"View: {'White' if self.game_state.board.is_white_perspective else 'Black'}'s perspective"
        )
        self.chessboard.draw_board(self.game_state.board.is_white_perspective)

    def toggle_coordinates(self):
        """Toggles coordinate visibility on the chessboard."""
        print("Toggle coordinates called in ChessTrainer")  # Debug print
        self.chessboard.toggle_coordinates(self.game_state.board.is_white_perspective)

    def save_statistics(self):
        """
        Handles the saving of game statistics to a file.
        Opens a file dialog for the user to choose the save location.
        """
        if not self.performance_tracker.has_data():
            tk.messagebox.showwarning(
                "No Data",
                "There are no statistics to save yet. Play some games first!"
            )
            return

        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Game Statistics"
        )

        if file_path:
            try:
                self.performance_tracker.save_statistics(file_path)
                tk.messagebox.showinfo(
                    "Success",
                    "Statistics saved successfully!"
                )
            except Exception as e:
                tk.messagebox.showerror(
                    "Error",
                    f"Failed to save statistics: {str(e)}"
                )

    def load_statistics(self):
        """
        Handles loading of game statistics from a file.
        Opens a file dialog for the user to select the statistics file.
        """
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Game Statistics"
        )

        if file_path:
            try:
                self.performance_tracker.load_statistics(file_path)

                # Update the visualizations with loaded data
                self.performance_tracker.update_visualizations()
                self.performance_graphs.refresh()

                # Show success message with timestamp
                stats_data = self.performance_tracker.get_last_timestamp()
                if stats_data:
                    tk.messagebox.showinfo(
                        "Success",
                        f"Statistics loaded successfully!\nData from: {stats_data}"
                    )
                else:
                    tk.messagebox.showinfo(
                        "Success",
                        "Statistics loaded successfully!"
                    )

            except Exception as e:
                tk.messagebox.showerror(
                    "Error",
                    f"Failed to load statistics: {str(e)}"
                )

    def exit_application(self):
        """Closes the application."""
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Starts the main application loop."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = ChessTrainer()
    app.run()


if __name__ == "__main__":
    main()
