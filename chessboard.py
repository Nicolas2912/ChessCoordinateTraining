import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
from tkinter import filedialog, messagebox


class ChessCoordinatesGame:
    # Constants
    GRID_SIZE = 8
    TILE_SIZE = 60

    COLORS = {
        'primary': '#1a365d',  # Dark blue
        'secondary': '#2d3748',  # Dark gray
        'white_square': '#f7fafc',  # Light gray-white
        'black_square': '#4a5568',  # Medium gray
        'accent': '#3182ce',  # Bright blue
        'text': '#2d3748',  # Dark gray
        'background': '#ffffff'  # White
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chessboard Coordinates Practice")

        # Game state variables
        self.is_white_perspective = True
        self.coordinates_visible = False
        self.coordinates_text = {}
        self.current_coordinate = None
        self.is_game_active = False
        self.last_coordinate_time = 0

        # Statistics variables
        self.correct_clicks = 0
        self.wrong_clicks = 0
        self.total_response_time = 0
        self.fastest_response = float('inf')
        self.slowest_response = 0

        # History tracking
        self.score_history = []
        self.accuracy_history = []
        self.correct_clicks_history = []
        self.wrong_clicks_history = []
        self.avg_time_history = []
        self.fastest_time_history = []
        self.slowest_time_history = []

        self.setup_ui()
        self.setup_matplotlib()
        self.draw_chessboard()

    def setup_ui(self):
        """Initialize all UI components"""
        self.root.configure(bg=self.COLORS['background'])
        self.root.option_add('*Font', 'Helvetica 10')

        # Create main frames
        self.right_frame = tk.Frame(self.root, bg=self.COLORS['background'])
        self.right_frame.pack(side="right", padx=20, fill="both", expand=True)

        self.game_frame = tk.Frame(self.root, bg=self.COLORS['background'])
        self.game_frame.pack(side="left", padx=10, fill="both", expand=True)

        # Setup perspective label
        self.perspective_label = tk.Label(
            self.game_frame,
            text="View: White's perspective",
            font=("Helvetica", 14, "bold"),
            fg=self.COLORS['primary'],
            bg=self.COLORS['background']
        )

        # Setup coordinate display
        self.setup_coordinate_display()

        # Setup canvas
        self.canvas = tk.Canvas(
            self.game_frame,
            width=self.GRID_SIZE * self.TILE_SIZE + 100,
            height=self.GRID_SIZE * self.TILE_SIZE
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.check_coordinate)

        # Setup control panel
        self.setup_control_panel()

        self.perspective_label.pack(pady=5)

    def setup_coordinate_display(self):
        """Setup the coordinate display frame and label"""
        self.coord_display_frame = tk.Frame(
            self.game_frame,
            width=self.GRID_SIZE * self.TILE_SIZE + 100,
            height=40,
            bg=self.COLORS['background'],
            highlightbackground=self.COLORS['secondary'],
            highlightthickness=1,
            relief="ridge",
            bd=0
        )
        self.coord_display_frame.pack(pady=10)
        self.coord_display_frame.pack_propagate(False)

        self.coord_label = tk.Label(
            self.coord_display_frame,
            text="Click Start to begin",
            font=("Helvetica", 24, "bold"),
            fg=self.COLORS['accent'],
            bg=self.COLORS['background']
        )
        self.coord_label.pack(expand=True, fill="both")

    def setup_matplotlib(self):
        """Initialize matplotlib figures and graphs"""
        self.fig = plt.figure(figsize=(8, 6))
        plt.subplots_adjust(hspace=0.5, wspace=0.3)

        # Create subplots
        self.ax_score = plt.subplot(221)
        self.ax_accuracy = plt.subplot(222)
        self.ax_clicks = plt.subplot(223)
        self.ax_time = plt.subplot(224)

        # Setup base styling
        for ax in [self.ax_score, self.ax_accuracy, self.ax_clicks, self.ax_time]:
            ax.tick_params(labelsize=8)
            ax.title.set_fontsize(10)
            ax.xaxis.label.set_fontsize(8)
            ax.yaxis.label.set_fontsize(8)

        # Create graph canvas
        self.canvas_graph = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas_widget = self.canvas_graph._tkcanvas
        self.canvas_widget.pack(expand=True)

    def setup_control_panel(self):
        """Setup the control panel with all game controls and statistics"""
        # Create frames
        self.control_panel = tk.Frame(self.right_frame, bg=self.COLORS['background'])
        self.control_panel.pack(side="bottom", pady=10)

        self.stats_frame = tk.Frame(self.control_panel, bg=self.COLORS['background'])
        self.stats_frame.pack(pady=10)

        self.timer_control_frame = tk.Frame(self.control_panel, bg=self.COLORS['background'])
        self.timer_control_frame.pack(pady=5)

        self.button_frame = tk.Frame(self.control_panel, bg=self.COLORS['background'])
        self.button_frame.pack(pady=5)

        # Create statistics labels
        self.setup_stat_labels()

        # Create game controls
        self.setup_game_controls()

    def setup_stat_labels(self):
        """Setup all statistics labels"""
        self.correct_label = tk.Label(self.stats_frame, text="Correct: 0")
        self.wrong_label = tk.Label(self.stats_frame, text="Wrong: 0")
        self.accuracy_label = tk.Label(self.stats_frame, text="Accuracy: 0%")
        self.avg_time_label = tk.Label(self.stats_frame, text="Avg Time: 0.0s")
        self.score_label = tk.Label(self.control_panel, text="Score: 0")

        # Pack and style labels
        for label in [self.correct_label, self.wrong_label, self.accuracy_label, self.avg_time_label]:
            label.pack(side="left", padx=5)
            label.configure(
                font=("Helvetica", 10),
                fg=self.COLORS['primary'],
                bg=self.COLORS['background']
            )

        self.score_label.pack(pady=5)
        self.score_label.configure(
            font=("Helvetica", 14, "bold"),
            fg=self.COLORS['primary'],
            bg=self.COLORS['background']
        )

    def setup_game_controls(self):
        """Setup game control buttons and timer"""
        # Create duration slider
        self.duration_var = tk.IntVar(value=30)
        self.duration_slider = tk.Scale(
            self.timer_control_frame,
            from_=5,
            to=60,
            orient='horizontal',
            length=150,
            variable=self.duration_var,
            label='Game Duration (s)',
            resolution=1
        )
        self.duration_slider.pack(side='left', padx=5)

        # Create timer label
        self.timer_label = tk.Label(
            self.timer_control_frame,
            text="Time Left: 30s",
            font=("Helvetica", 12),
            fg=self.COLORS['primary'],
            bg=self.COLORS['background']
        )
        self.timer_label.pack(side='left', padx=5)

        # Create control buttons
        self.create_control_buttons()

    def create_control_buttons(self):
        """Create and style all control buttons"""
        buttons = [
            {"text": "Start", "command": self.start_timer, "color": self.COLORS['accent']},
            {"text": "Flip Board", "command": self.flip_board, "color": self.COLORS['accent']},
            {"text": "Show Coordinates", "command": self.toggle_coordinates, "color": self.COLORS['accent']},
            {"text": "Save Stats", "command": self.save_stats, "color": self.COLORS['accent']},
            {"text": "Load Stats", "command": self.load_stats, "color": self.COLORS['accent']},
            {"text": "Exit", "command": self.exit_program, "color": '#dc2626'}  # Red color for exit button
        ]

        for button_config in buttons:
            button = tk.Button(
                self.button_frame,
                text=button_config["text"],
                command=button_config["command"],
                font=("Helvetica", 10, "bold"),
                bg=button_config["color"],
                fg='white',
                relief="flat",
                padx=15,
                pady=5,
                cursor="hand2"
            )
            button.pack(side="left", padx=2)

    def exit_program(self):
        """Exit the program with confirmation"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            self.root.destroy()

    def save_stats(self):
        """Save game statistics to a JSON file"""
        if not any([self.score_history, self.accuracy_history, self.correct_clicks_history]):
            messagebox.showwarning("No Data", "There are no statistics to save yet. Play some games first!")
            return

        # Create statistics dictionary
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

        # Open file dialog for saving
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Game Statistics"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(stats_data, f, indent=4)
                messagebox.showinfo("Success", "Statistics saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save statistics: {str(e)}")

    def load_stats(self):
        """Load game statistics from a JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Game Statistics"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    stats_data = json.load(f)

                # Update all history lists
                self.score_history = stats_data['score_history']
                self.accuracy_history = stats_data['accuracy_history']
                self.correct_clicks_history = stats_data['correct_clicks_history']
                self.wrong_clicks_history = stats_data['wrong_clicks_history']
                self.avg_time_history = stats_data['avg_time_history']
                self.fastest_time_history = stats_data['fastest_time_history']
                self.slowest_time_history = stats_data['slowest_time_history']

                # Update the graphs
                self.update_score_graph()
                messagebox.showinfo("Success", "Statistics loaded successfully!")

                # Show load timestamp if available
                if 'timestamp' in stats_data:
                    messagebox.showinfo("File Info", f"Statistics from: {stats_data['timestamp']}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")

    # Game Logic Methods
    def draw_chessboard(self):
        """Draw the chessboard with current perspective"""
        self.canvas.delete("all")

        # Add background
        self.canvas.create_rectangle(
            0, 0,
            self.GRID_SIZE * self.TILE_SIZE, self.GRID_SIZE * self.TILE_SIZE,
            fill=self.COLORS['background'],
            width=2,
            outline=self.COLORS['secondary']
        )

        # Draw squares
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                actual_row = row if self.is_white_perspective else (self.GRID_SIZE - 1 - row)
                actual_col = col if self.is_white_perspective else (self.GRID_SIZE - 1 - col)

                color = self.COLORS['white_square'] if (actual_row + actual_col) % 2 == 0 else self.COLORS[
                    'black_square']

                self.canvas.create_rectangle(
                    col * self.TILE_SIZE + 1, row * self.TILE_SIZE + 1,
                    (col + 1) * self.TILE_SIZE - 1, (row + 1) * self.TILE_SIZE - 1,
                    fill=color,
                    outline="",
                    width=0
                )

        # Draw file letters
        for i in range(self.GRID_SIZE):
            file_letter = chr(ord('A') + i) if self.is_white_perspective else chr(ord('A') + (self.GRID_SIZE - 1 - i))
            self.canvas.create_text(
                i * self.TILE_SIZE + self.TILE_SIZE / 2,
                self.GRID_SIZE * self.TILE_SIZE + 20,
                text=file_letter,
                font=("Helvetica", 12, "bold"),
                fill=self.COLORS['primary']
            )

    def flip_board(self):
        """Flip the board perspective"""
        self.is_white_perspective = not self.is_white_perspective
        self.perspective_label.config(
            text=f"View: {'White' if self.is_white_perspective else 'Black'}'s perspective"
        )
        self.draw_chessboard()
        if self.coordinates_visible:
            self.toggle_coordinates()
            self.toggle_coordinates()

    def toggle_coordinates(self):
        """Toggle coordinate visibility on the board"""
        if self.coordinates_visible:
            for text_id in self.coordinates_text.values():
                self.canvas.delete(text_id)
            self.coordinates_text.clear()
        else:
            for row in range(self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    coord_text = self.get_coordinate_text(col, row)
                    text_color = "white" if (row + col) % 2 == 1 else "black"

                    text_id = self.canvas.create_text(
                        col * self.TILE_SIZE + self.TILE_SIZE / 2,
                        row * self.TILE_SIZE + self.TILE_SIZE / 2,
                        text=coord_text,
                        font=("Arial", 12),
                        fill=text_color
                    )
                    self.coordinates_text[(col, row)] = text_id

        self.coordinates_visible = not self.coordinates_visible

    def get_coordinate_text(self, col, row):
        """Get the correct coordinate text based on perspective"""
        if self.is_white_perspective:
            letter = chr(ord('A') + col)
            number = self.GRID_SIZE - row
        else:
            letter = chr(ord('A') + (self.GRID_SIZE - 1 - col))
            number = row + 1
        return f"{letter}{number}"

    def generate_random_coordinate(self):
        """Generate a random coordinate and return its notation and screen position"""
        file = random.randint(0, 7)
        rank = random.randint(1, 8)
        algebraic = f"{chr(ord('A') + file)}{rank}"
        screen_col = file
        screen_row = 8 - rank
        return algebraic, screen_col, screen_row

    def update_random_coordinate(self):
        """Update the display with a new random coordinate"""
        coord, col, row = self.generate_random_coordinate()
        self.current_coordinate = (col, row)
        self.coord_label.config(text=coord)
        self.last_coordinate_time = time.time()

    def check_coordinate(self, event):
        """Handle mouse clicks on the chessboard"""
        if self.current_coordinate is None or not self.is_game_active:
            return

        raw_clicked_col = event.x // self.TILE_SIZE
        raw_clicked_row = event.y // self.TILE_SIZE

        target_col, target_row = self.current_coordinate
        if not self.is_white_perspective:
            target_col = self.GRID_SIZE - 1 - target_col
            target_row = self.GRID_SIZE - 1 - target_row

        response_time = time.time() - self.last_coordinate_time

        if (raw_clicked_col, raw_clicked_row) == (target_col, target_row):
            self.correct_clicks += 1
            self.total_response_time += response_time
            self.fastest_response = min(self.fastest_response, response_time)
            self.slowest_response = max(self.slowest_response, response_time)
            self.update_random_coordinate()
        else:
            self.wrong_clicks += 1

    def update_stats(self):
        """Update all statistics labels with current values"""
        total_clicks = self.correct_clicks + self.wrong_clicks
        accuracy = (self.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        avg_time = (self.total_response_time / self.correct_clicks) if self.correct_clicks > 0 else 0

        self.correct_label.config(text=f"Correct: {self.correct_clicks}")
        self.wrong_label.config(text=f"Wrong: {self.wrong_clicks}")
        self.accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")
        self.avg_time_label.config(text=f"Avg Time: {avg_time:.2f}s")
        self.score_label.config(text=f"Score: {self.calculate_score()}")

    def calculate_score(self):
        """Calculate the current score based on correct clicks"""
        """Calculate the player's score based on performance"""
        if self.correct_clicks == 0:
            return 0

        # Base score from correct clicks (100 points each)
        base_score = self.correct_clicks * 100

        # Accuracy bonus (up to 100% bonus)
        accuracy = self.correct_clicks / max(1, (self.correct_clicks + self.wrong_clicks))
        accuracy_bonus = base_score * accuracy

        # Speed bonus based on average response time
        avg_response_time = self.total_response_time / self.correct_clicks
        speed_bonus = max(0, 500 - (avg_response_time * 100))  # Faster times give higher bonus

        # Penalty for wrong clicks (50 points each)
        penalties = self.wrong_clicks * 50

        return int(base_score + accuracy_bonus + speed_bonus - penalties)

    def show_final_results(self):
        """Display the final results window with statistics"""
        # Calculate final statistics
        final_score = self.calculate_score()
        total_clicks = self.correct_clicks + self.wrong_clicks
        accuracy = (self.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        avg_time = (self.total_response_time / self.correct_clicks) if self.correct_clicks > 0 else 0

        # Add statistics to histories
        self.score_history.append(final_score)
        self.accuracy_history.append(accuracy)
        self.correct_clicks_history.append(self.correct_clicks)
        self.wrong_clicks_history.append(self.wrong_clicks)
        self.avg_time_history.append(avg_time)
        self.fastest_time_history.append(self.fastest_response if self.fastest_response != float('inf') else 0)
        self.slowest_time_history.append(self.slowest_response)

        # Update graphs
        self.update_score_graph()

        # Create results window
        result_window = tk.Toplevel(self.root)
        result_window.title("Game Results")

        # Add statistics labels
        tk.Label(result_window, text="Final Results", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(result_window, text=f"Final Score: {final_score}", font=("Arial", 14)).pack()
        tk.Label(result_window, text=f"Total Clicks: {total_clicks}", font=("Arial", 12)).pack()
        tk.Label(result_window, text=f"Correct Clicks: {self.correct_clicks}", font=("Arial", 12)).pack()
        tk.Label(result_window, text=f"Wrong Clicks: {self.wrong_clicks}", font=("Arial", 12)).pack()
        tk.Label(result_window, text=f"Accuracy: {accuracy:.1f}%", font=("Arial", 12)).pack()
        tk.Label(result_window, text=f"Average Response Time: {avg_time:.2f}s", font=("Arial", 12)).pack()
        if self.correct_clicks > 0:
            tk.Label(result_window, text=f"Fastest Response: {self.fastest_response:.2f}s", font=("Arial", 12)).pack()
            tk.Label(result_window, text=f"Slowest Response: {self.slowest_response:.2f}s", font=("Arial", 12)).pack()

    def update_score_graph(self):
        """Update all statistics graphs"""
        # Clear all subplots
        self.ax_score.clear()
        self.ax_accuracy.clear()
        self.ax_clicks.clear()
        self.ax_time.clear()

        if self.score_history:
            x_labels = [f"Game {i + 1}" for i in range(len(self.score_history))]

            # Score History
            self.ax_score.plot(x_labels, self.score_history, 'b-o', label='Score')
            for i, score in enumerate(self.score_history):
                self.ax_score.text(i, score, f'{score}', ha='center', va='bottom')
            self.ax_score.set_title('Score History')
            self.ax_score.set_xlabel('Games')
            self.ax_score.set_ylabel('Score')
            self.ax_score.grid(True, linestyle='--', alpha=0.7)

            # Accuracy History
            self.ax_accuracy.plot(x_labels, self.accuracy_history, 'g-o', label='Accuracy')
            for i, acc in enumerate(self.accuracy_history):
                self.ax_accuracy.text(i, acc, f'{acc:.1f}%', ha='center', va='bottom')
            self.ax_accuracy.set_title('Accuracy History')
            self.ax_accuracy.set_xlabel('Games')
            self.ax_accuracy.set_ylabel('Accuracy (%)')
            self.ax_accuracy.grid(True, linestyle='--', alpha=0.7)

            # Clicks History
            self.ax_clicks.plot(x_labels, self.correct_clicks_history, 'g-o', label='Correct')
            self.ax_clicks.plot(x_labels, self.wrong_clicks_history, 'r-o', label='Wrong')
            self.ax_clicks.set_title('Clicks History')
            self.ax_clicks.set_xlabel('Games')
            self.ax_clicks.set_ylabel('Number of Clicks')
            self.ax_clicks.legend()
            self.ax_clicks.grid(True, linestyle='--', alpha=0.7)

            # Response Times
            self.ax_time.plot(x_labels, self.avg_time_history, 'b-o', label='Average')
            self.ax_time.plot(x_labels, self.fastest_time_history, 'g-o', label='Fastest')
            self.ax_time.plot(x_labels, self.slowest_time_history, 'r-o', label='Slowest')
            self.ax_time.set_title('Response Times')
            self.ax_time.set_xlabel('Games')
            self.ax_time.set_ylabel('Time (seconds)')
            self.ax_time.legend()
            self.ax_time.grid(True, linestyle='--', alpha=0.7)

            # Rotate x-axis labels for all subplots
            for ax in [self.ax_score, self.ax_accuracy, self.ax_clicks, self.ax_time]:
                ax.tick_params(axis='x', rotation=45)

            plt.tight_layout()

        self.canvas_graph.draw()

    def start_timer(self):
        """Start the game timer and reset statistics"""
        # Reset all statistics
        self.correct_clicks = 0
        self.wrong_clicks = 0
        self.total_response_time = 0
        self.fastest_response = float('inf')
        self.slowest_response = 0
        self.is_game_active = True

        # Reset display
        self.update_stats()

        # Show first coordinate
        self.update_random_coordinate()

        def update_timer():
            nonlocal time_left
            if time_left > 0:
                time_left -= 1
                self.timer_label.config(text=f"Time Left: {time_left}s")
                self.root.after(1000, update_timer)
            else:
                self.timer_label.config(text="Time's up!")
                self.coord_label.config(text="Game Over!")
                self.is_game_active = False
                self.root.after(100, self.show_final_results)

        time_left = self.duration_var.get()
        update_timer()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = ChessCoordinatesGame()
    game.run()
