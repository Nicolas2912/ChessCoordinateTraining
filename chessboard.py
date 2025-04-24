import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime

# Define the chessboard grid size
GRID_SIZE = 8
TILE_SIZE = 60  # Size of each square

# Create the main window
root = tk.Tk()
root.title("Chessboard Coordinates Practice")

# Variables for board state
is_white_perspective = True
coordinates_visible = False
coordinates_text = {}  # Dictionary to store coordinate text objects

COLORS = {
    'primary': '#1a365d',  # Dark blue
    'secondary': '#2d3748', # Dark gray
    'white_square': '#f7fafc',  # Light gray-white
    'black_square': '#4a5568',  # Medium gray
    'accent': '#3182ce',  # Bright blue
    'text': '#2d3748',  # Dark gray
    'background': '#ffffff'  # White
}

# Update the main window styling
root.configure(bg=COLORS['background'])
root.option_add('*Font', 'Helvetica 10')

# Update the frames
right_frame = tk.Frame(root, bg=COLORS['background'])
right_frame.pack(side="right", padx=20, fill="both", expand=True)

game_frame = tk.Frame(root, bg=COLORS['background'])
game_frame.pack(side="left", padx=10, fill="both", expand=True)

# Update the perspective label
perspective_label = tk.Label(
    game_frame, 
    text="View: White's perspective", 
    font=("Helvetica", 14, "bold"),
    fg=COLORS['primary'],
    bg=COLORS['background']
)

# Update the coordinate display frame with rounded corners and shadow effect
coord_display_frame = tk.Frame(
    game_frame, 
    width=GRID_SIZE * TILE_SIZE + 100, 
    height=40, 
    bg=COLORS['background'],
    highlightbackground=COLORS['secondary'],
    highlightthickness=1,
    relief="ridge",
    bd=0
)
coord_display_frame.pack(pady=10)
coord_display_frame.pack_propagate(False)

# Update the coordinate label
coord_label = tk.Label(
    coord_display_frame, 
    text="Click Start to begin", 
    font=("Helvetica", 24, "bold"), 
    fg=COLORS['accent'],
    bg=COLORS['background']
)
coord_label.pack(expand=True, fill="both")

# NOW pack the perspective label
perspective_label.pack(pady=5)  # Pack this SECOND

# Create a Canvas widget to draw the chessboard
canvas = tk.Canvas(game_frame, width=GRID_SIZE * TILE_SIZE + 100, height=GRID_SIZE * TILE_SIZE)
canvas.pack()

# Create matplotlib figure for statistics
fig = plt.figure(figsize=(8, 6))
plt.subplots_adjust(hspace=0.5, wspace=0.3)

# Create subplots
ax_score = plt.subplot(221)  # Score history
ax_accuracy = plt.subplot(222)  # Accuracy history
ax_clicks = plt.subplot(223)  # Correct vs Wrong clicks
ax_time = plt.subplot(224)  # Response times

# Setup base styling for all subplots
for ax in [ax_score, ax_accuracy, ax_clicks, ax_time]:
    ax.tick_params(labelsize=8)
    ax.title.set_fontsize(10)
    ax.xaxis.label.set_fontsize(8)
    ax.yaxis.label.set_fontsize(8)

# Initialize history lists for statistics
score_history = []
accuracy_history = []
correct_clicks_history = []
wrong_clicks_history = []
avg_time_history = []
fastest_time_history = []
slowest_time_history = []

# Create the graph canvas
canvas_graph = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas_graph._tkcanvas
canvas_widget.pack(expand=True)

def get_coordinate_text(col, row):
    """Get the correct coordinate text based on perspective"""
    if is_white_perspective:
        letter = chr(ord('A') + col)
        number = GRID_SIZE - row
    else:
        letter = chr(ord('A') + (GRID_SIZE - 1 - col))
        number = row + 1
    return f"{letter}{number}"

def flip_board():
    global is_white_perspective
    is_white_perspective = not is_white_perspective
    perspective_label.config(text=f"View: {'White' if is_white_perspective else 'Black'}'s perspective")
    draw_chessboard()
    if coordinates_visible:
        toggle_coordinates()  # Remove old coordinates
        toggle_coordinates()  # Draw new coordinates

def toggle_coordinates():
    global coordinates_visible
    
    if coordinates_visible:
        for text_id in coordinates_text.values():
            canvas.delete(text_id)
        coordinates_text.clear()
    else:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord_text = get_coordinate_text(col, row)
                text_color = "white" if (row + col) % 2 == 1 else "black"
                
                text_id = canvas.create_text(
                    col * TILE_SIZE + TILE_SIZE / 2,
                    row * TILE_SIZE + TILE_SIZE / 2,
                    text=coord_text,
                    font=("Arial", 12),
                    fill=text_color
                )
                coordinates_text[(col, row)] = text_id
    
    coordinates_visible = not coordinates_visible

# Update the draw_chessboard function
def draw_chessboard():
    canvas.delete("all")
    
    # Add a background rectangle with rounded corners
    canvas.create_rectangle(
        0, 0, 
        GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE,
        fill=COLORS['background'],
        width=2,
        outline=COLORS['secondary']
    )
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            actual_row = row if is_white_perspective else (GRID_SIZE - 1 - row)
            actual_col = col if is_white_perspective else (GRID_SIZE - 1 - col)
            
            color = COLORS['white_square'] if (actual_row + actual_col) % 2 == 0 else COLORS['black_square']
            
            # Draw squares with slight padding for a modern look
            canvas.create_rectangle(
                col * TILE_SIZE + 1, row * TILE_SIZE + 1,
                (col + 1) * TILE_SIZE - 1, (row + 1) * TILE_SIZE - 1,
                fill=color,
                outline="",  # Remove outline for cleaner look
                width=0
            )
    
    # Update file letters style
    for i in range(GRID_SIZE):
        file_letter = chr(ord('A') + i) if is_white_perspective else chr(ord('A') + (GRID_SIZE - 1 - i))
        canvas.create_text(
            i * TILE_SIZE + TILE_SIZE/2,
            GRID_SIZE * TILE_SIZE + 20,
            text=file_letter,
            font=("Helvetica", 12, "bold"),
            fill=COLORS['primary']
        )

# Game state variables
current_coordinate = None
is_game_active = False
last_coordinate_time = 0
correct_clicks = 0
wrong_clicks = 0
total_response_time = 0
fastest_response = float('inf')
slowest_response = 0

def generate_random_coordinate():
    """Generate a random coordinate and return its notation and screen position"""
    # Step 1: Generate a random chess coordinate
    file = random.randint(0, 7)  # 0-7 representing A-H
    rank = random.randint(1, 8)  # 1-8 representing chess ranks
    
    # Step 2: Create algebraic notation (e.g., "D6")
    algebraic = f"{chr(ord('A') + file)}{rank}"
    
    # Step 3: Convert to screen coordinates
    screen_col = file
    screen_row = 8 - rank  # Convert chess rank to screen row (0 at top)
    
    return algebraic, screen_col, screen_row

def update_random_coordinate():
    """Update the display with a new random coordinate"""
    global current_coordinate, last_coordinate_time
    coord, col, row = generate_random_coordinate()
    current_coordinate = (col, row)
    coord_label.config(text=coord)
    last_coordinate_time = time.time()

def calculate_score():
    """Calculate the player's score based on performance"""
    if correct_clicks == 0:
        return 0
    
    # Base score from correct clicks (100 points each)
    base_score = correct_clicks * 100
    
    # Accuracy bonus (up to 100% bonus)
    accuracy = correct_clicks / max(1, (correct_clicks + wrong_clicks))
    accuracy_bonus = base_score * accuracy
    
    # Speed bonus based on average response time
    avg_response_time = total_response_time / correct_clicks
    speed_bonus = max(0, 500 - (avg_response_time * 100))  # Faster times give higher bonus
    
    # Penalty for wrong clicks (50 points each)
    penalties = wrong_clicks * 50
    
    return int(base_score + accuracy_bonus + speed_bonus - penalties)

def update_stats():
    """Update the display of game statistics"""
    correct_label.config(text=f"Correct: {correct_clicks}")
    wrong_label.config(text=f"Wrong: {wrong_clicks}")
    
    total_clicks = correct_clicks + wrong_clicks
    accuracy = (correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
    accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")
    
    avg_time = (total_response_time / correct_clicks) if correct_clicks > 0 else 0
    avg_time_label.config(text=f"Avg Time: {avg_time:.2f}s")
    
    score_label.config(text=f"Score: {calculate_score()}")

def check_coordinate(event):
    """Handle mouse clicks on the chessboard"""
    if current_coordinate is None or not is_game_active:
        return
    
    global correct_clicks, wrong_clicks, total_response_time, fastest_response, slowest_response
    
    # Get raw click position
    raw_clicked_col = event.x // TILE_SIZE
    raw_clicked_row = event.y // TILE_SIZE
    
    # Get the target coordinate we're looking for (adjusted for perspective)
    target_col, target_row = current_coordinate
    if not is_white_perspective:
        target_col = GRID_SIZE - 1 - target_col
        target_row = GRID_SIZE - 1 - target_row
    
    response_time = time.time() - last_coordinate_time
    
    # Compare the raw click with the adjusted target
    if (raw_clicked_col, raw_clicked_row) == (target_col, target_row):
        correct_clicks += 1
        total_response_time += response_time
        fastest_response = min(fastest_response, response_time)
        slowest_response = max(slowest_response, response_time)
        update_random_coordinate()
    else:
        wrong_clicks += 1
    
    update_stats()

def show_final_results():
    """Display the final results window with statistics"""
    # Calculate final statistics
    final_score = calculate_score()
    total_clicks = correct_clicks + wrong_clicks
    accuracy = (correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
    avg_time = (total_response_time / correct_clicks) if correct_clicks > 0 else 0
    
    # Add statistics to histories
    score_history.append(final_score)
    accuracy_history.append(accuracy)
    correct_clicks_history.append(correct_clicks)
    wrong_clicks_history.append(wrong_clicks)
    avg_time_history.append(avg_time)
    fastest_time_history.append(fastest_response if fastest_response != float('inf') else 0)
    slowest_time_history.append(slowest_response)
    
    # Update graphs
    update_score_graph()
    
    # Create results window
    result_window = tk.Toplevel(root)
    result_window.title("Game Results")
    
    # Add statistics labels
    tk.Label(result_window, text="Final Results", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(result_window, text=f"Final Score: {final_score}", font=("Arial", 14)).pack()
    tk.Label(result_window, text=f"Total Clicks: {total_clicks}", font=("Arial", 12)).pack()
    tk.Label(result_window, text=f"Correct Clicks: {correct_clicks}", font=("Arial", 12)).pack()
    tk.Label(result_window, text=f"Wrong Clicks: {wrong_clicks}", font=("Arial", 12)).pack()
    tk.Label(result_window, text=f"Accuracy: {accuracy:.1f}%", font=("Arial", 12)).pack()
    tk.Label(result_window, text=f"Average Response Time: {avg_time:.2f}s", font=("Arial", 12)).pack()
    if correct_clicks > 0:
        tk.Label(result_window, text=f"Fastest Response: {fastest_response:.2f}s", font=("Arial", 12)).pack()
        tk.Label(result_window, text=f"Slowest Response: {slowest_response:.2f}s", font=("Arial", 12)).pack()

def start_timer():
    """Start the game timer and reset statistics"""
    global correct_clicks, wrong_clicks, total_response_time, fastest_response, slowest_response, is_game_active
    
    # Reset all statistics
    correct_clicks = 0
    wrong_clicks = 0
    total_response_time = 0
    fastest_response = float('inf')
    slowest_response = 0
    is_game_active = True
    
    # Reset display
    update_stats()
    
    # Show first coordinate
    update_random_coordinate()
    
    def update_timer():
        nonlocal time_left
        if time_left > 0:
            time_left -= 1
            timer_label.config(text=f"Time Left: {time_left}s")
            root.after(1000, update_timer)
        else:
            timer_label.config(text="Time's up!")
            coord_label.config(text="Game Over!")
            global is_game_active
            is_game_active = False
            root.after(100, show_final_results)
    
    time_left = duration_var.get()
    update_timer()

def update_score_graph():
    """Update all statistics graphs"""
    # Clear all subplots
    ax_score.clear()
    ax_accuracy.clear()
    ax_clicks.clear()
    ax_time.clear()
    
    if score_history:
        x_labels = [f"Game {i+1}" for i in range(len(score_history))]
        
        # Score History
        ax_score.plot(x_labels, score_history, 'b-o', label='Score')
        for i, score in enumerate(score_history):
            ax_score.text(i, score, f'{score}', ha='center', va='bottom')
        ax_score.set_title('Score History')
        ax_score.set_xlabel('Games')
        ax_score.set_ylabel('Score')
        ax_score.grid(True, linestyle='--', alpha=0.7)
        
        # Accuracy History
        ax_accuracy.plot(x_labels, accuracy_history, 'g-o', label='Accuracy')
        for i, acc in enumerate(accuracy_history):
            ax_accuracy.text(i, acc, f'{acc:.1f}%', ha='center', va='bottom')
        ax_accuracy.set_title('Accuracy History')
        ax_accuracy.set_xlabel('Games')
        ax_accuracy.set_ylabel('Accuracy (%)')
        ax_accuracy.grid(True, linestyle='--', alpha=0.7)
        
        # Clicks History
        ax_clicks.plot(x_labels, correct_clicks_history, 'g-o', label='Correct')
        ax_clicks.plot(x_labels, wrong_clicks_history, 'r-o', label='Wrong')
        ax_clicks.set_title('Clicks History')
        ax_clicks.set_xlabel('Games')
        ax_clicks.set_ylabel('Number of Clicks')
        ax_clicks.legend()
        ax_clicks.grid(True, linestyle='--', alpha=0.7)
        
        # Response Times
        ax_time.plot(x_labels, avg_time_history, 'b-o', label='Average')
        ax_time.plot(x_labels, fastest_time_history, 'g-o', label='Fastest')
        ax_time.plot(x_labels, slowest_time_history, 'r-o', label='Slowest')
        ax_time.set_title('Response Times')
        ax_time.set_xlabel('Games')
        ax_time.set_ylabel('Time (seconds)')
        ax_time.legend()
        ax_time.grid(True, linestyle='--', alpha=0.7)
        
        # Rotate x-axis labels for all subplots
        for ax in [ax_score, ax_accuracy, ax_clicks, ax_time]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
    
    canvas_graph.draw()

# Update the control panel styling
control_panel = tk.Frame(right_frame, bg=COLORS['background'])
control_panel.pack(side="bottom", pady=10)

# Update the stats frame
stats_frame = tk.Frame(control_panel, bg=COLORS['background'])
stats_frame.pack(pady=10)

# Create timer control frame
timer_control_frame = tk.Frame(control_panel, bg=COLORS['background'])
timer_control_frame.pack(pady=5)

# Create button frame
button_frame = tk.Frame(control_panel, bg=COLORS['background'])
button_frame.pack(pady=5)

# Create labels for statistics
correct_label = tk.Label(stats_frame, text="Correct: 0", font=("Arial", 10))
correct_label.pack(side="left", padx=5)

wrong_label = tk.Label(stats_frame, text="Wrong: 0", font=("Arial", 10))
wrong_label.pack(side="left", padx=5)

accuracy_label = tk.Label(stats_frame, text="Accuracy: 0%", font=("Arial", 10))
accuracy_label.pack(side="left", padx=5)

avg_time_label = tk.Label(stats_frame, text="Avg Time: 0.0s", font=("Arial", 10))
avg_time_label.pack(side="left", padx=5)

# Create score label
score_label = tk.Label(control_panel, text="Score: 0", font=("Arial", 12, "bold"))
score_label.pack(pady=5)

# Create duration slider
duration_var = tk.IntVar(value=30)
duration_slider = tk.Scale(
    timer_control_frame,
    from_=5,
    to=60,
    orient='horizontal',
    length=150,
    variable=duration_var,
    label='Game Duration (s)',
    resolution=1
)
duration_slider.pack(side='left', padx=5)

# Create timer label
timer_label = tk.Label(timer_control_frame, text="Time Left: 30s", font=("Arial", 12))
timer_label.pack(side='left', padx=5)

# Update all stat labels styling
for label in [correct_label, wrong_label, accuracy_label, avg_time_label]:
    label.configure(
        font=("Helvetica", 10),
        fg=COLORS['primary'],
        bg=COLORS['background']
    )

# Create modern button style function
def create_modern_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Helvetica", 10, "bold"),
        bg=COLORS['accent'],
        fg='white',
        relief="flat",
        padx=15,
        pady=5,
        cursor="hand2"  # Hand cursor on hover
    )

# Create buttons with modern styling
start_button = create_modern_button(button_frame, "Start", start_timer)
start_button.pack(side="left", padx=2)

flip_button = create_modern_button(button_frame, "Flip Board", flip_board)
flip_button.pack(side="left", padx=2)

toggle_button = create_modern_button(button_frame, "Show Coordinates", toggle_coordinates)
toggle_button.pack(side="left", padx=2)

# Update the score label styling
score_label.configure(
    font=("Helvetica", 14, "bold"),
    fg=COLORS['primary'],
    bg=COLORS['background']
)

# Update the timer label styling
timer_label.configure(
    font=("Helvetica", 12),
    fg=COLORS['primary'],
    bg=COLORS['background']
)

# Style the duration slider
duration_slider.configure(
    bg=COLORS['background'],
    troughcolor=COLORS['secondary'],
    activebackground=COLORS['accent']
)

# Draw initial board
draw_chessboard()

# Bind mouse click
canvas.bind("<Button-1>", check_coordinate)

# Start Tkinter event loop
root.mainloop()# Update the control panel styling
control_panel = tk.Frame(right_frame, bg=COLORS['background'])
control_panel.pack(side="bottom", pady=10)

# Update the stats frame
stats_frame = tk.Frame(control_panel, bg=COLORS['background'])
stats_frame.pack(pady=10)

# Create timer control frame
timer_control_frame = tk.Frame(control_panel, bg=COLORS['background'])
timer_control_frame.pack(pady=5)

# Create button frame
button_frame = tk.Frame(control_panel, bg=COLORS['background'])
button_frame.pack(pady=5)

# Create labels for statistics
correct_label = tk.Label(stats_frame, text="Correct: 0", font=("Arial", 10))
correct_label.pack(side="left", padx=5)

wrong_label = tk.Label(stats_frame, text="Wrong: 0", font=("Arial", 10))
wrong_label.pack(side="left", padx=5)

accuracy_label = tk.Label(stats_frame, text="Accuracy: 0%", font=("Arial", 10))
accuracy_label.pack(side="left", padx=5)

avg_time_label = tk.Label(stats_frame, text="Avg Time: 0.0s", font=("Arial", 10))
avg_time_label.pack(side="left", padx=5)

# Create score label
score_label = tk.Label(control_panel, text="Score: 0", font=("Arial", 12, "bold"))
score_label.pack(pady=5)

# Create duration slider
duration_var = tk.IntVar(value=30)
duration_slider = tk.Scale(
    timer_control_frame,
    from_=5,
    to=60,
    orient='horizontal',
    length=150,
    variable=duration_var,
    label='Game Duration (s)',
    resolution=1
)
duration_slider.pack(side='left', padx=5)

# Create timer label
timer_label = tk.Label(timer_control_frame, text="Time Left: 30s", font=("Arial", 12))
timer_label.pack(side='left', padx=5)

# Update all stat labels styling
for label in [correct_label, wrong_label, accuracy_label, avg_time_label]:
    label.configure(
        font=("Helvetica", 10),
        fg=COLORS['primary'],
        bg=COLORS['background']
    )

# Create modern button style function
def create_modern_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Helvetica", 10, "bold"),
        bg=COLORS['accent'],
        fg='white',
        relief="flat",
        padx=15,
        pady=5,
        cursor="hand2"  # Hand cursor on hover
    )

# Create buttons with modern styling
start_button = create_modern_button(button_frame, "Start", start_timer)
start_button.pack(side="left", padx=2)

flip_button = create_modern_button(button_frame, "Flip Board", flip_board)
flip_button.pack(side="left", padx=2)

toggle_button = create_modern_button(button_frame, "Show Coordinates", toggle_coordinates)
toggle_button.pack(side="left", padx=2)

# Update the score label styling
score_label.configure(
    font=("Helvetica", 14, "bold"),
    fg=COLORS['primary'],
    bg=COLORS['background']
)

# Update the timer label styling
timer_label.configure(
    font=("Helvetica", 12),
    fg=COLORS['primary'],
    bg=COLORS['background']
)

# Style the duration slider
duration_slider.configure(
    bg=COLORS['background'],
    troughcolor=COLORS['secondary'],
    activebackground=COLORS['accent']
)

# Draw initial board
draw_chessboard()

# Bind mouse click
canvas.bind("<Button-1>", check_coordinate)

# Start Tkinter event loop
root.mainloop()