# Chess Coordinates Trainer API Documentation

## Table of Contents
- [Core Module](#core-module)
  - [GameState](#gamestate)
  - [ChessBoardState](#chessboardstate)
  - [GamePerformance](#gameperformance)
  - [GameConfig](#gameconfig)
- [Statistics Module](#statistics-module)
  - [GameSession](#gamesession)
  - [PerformanceTracker](#performancetracker)
- [UI Components Module](#ui-components-module)
  - [ChessboardCanvas](#chessboardcanvas)
  - [CoordinateDisplay](#coordinatedisplay)
  - [StatisticsPanel](#statisticspanel)
  - [GameControls](#gamecontrols)
  - [PerformanceGraphs](#performancegraphs)
  - [UIConfig](#uiconfig)

## Core Module

### GameState
The central game state manager that coordinates board state and performance tracking.

#### Methods
```python
def __init__(self)
```
Initializes game state with board and performance tracking components.

```python
def start_game(self) -> None
```
Initializes a new game session.

```python
def end_game(self) -> None
```
Concludes the current game session and saves statistics.

```python
def get_save_data(self) -> Dict
```
Returns a dictionary containing all historical game data.

```python
def load_save_data(self, data: Dict) -> None
```
Loads saved game data from a dictionary.

### ChessBoardState
Manages the state and logic of the chess board.

#### Methods
```python
def flip_perspective(self) -> None
```
Toggles the board perspective between white and black sides.

```python
def generate_coordinate(self) -> Tuple[str, int, int]
```
Generates a random chess coordinate.
- Returns: (algebraic_notation, screen_col, screen_row)

```python
def validate_click(self, click_x: int, click_y: int) -> bool
```
Validates if a clicked position matches the target coordinate.

```python
def get_coordinate_notation(self, col: int, row: int) -> str
```
Converts board coordinates to algebraic notation.

### GamePerformance
Manages game performance tracking and scoring.

#### Methods
```python
def reset_session(self) -> None
```
Resets current session statistics.

```python
def record_attempt(self, is_correct: bool, response_time: float) -> None
```
Records the result of a move attempt.

```python
def calculate_score(self) -> int
```
Calculates the current session score based on performance metrics.

#### Scoring Formula
```python
score = base_score + accuracy_bonus + speed_bonus - penalties
where:
  base_score = correct_clicks * 100
  accuracy_bonus = base_score * (correct/total)
  speed_bonus = max(0, 500 - (avg_response_time * 100))
  penalties = wrong_clicks * 50
```

### GameConfig
Configuration settings for the chess coordinates game.

#### Properties
```python
GRID_SIZE: int = 8
TILE_SIZE: int = 60
MIN_DURATION: int = 5
MAX_DURATION: int = 60
DEFAULT_DURATION: int = 30
BASE_SCORE_PER_CORRECT: int = 100
PENALTY_PER_WRONG: int = 50
SPEED_BONUS_MAX: int = 500
```

## Statistics Module

### GameSession
Represents a single game session's statistics.

#### Methods
```python
def reset(self) -> None
```
Resets all session statistics to initial values.

```python
def record_attempt(self, correct: bool, response_time: float) -> None
```
Records a single attempt in the game session.

```python
def get_session_stats(self) -> dict
```
Returns current session statistics including score, accuracy, and timing metrics.

### PerformanceTracker
Tracks and analyzes long-term performance statistics.

#### Methods
```python
def initialize_visualization(self, figure: Figure) -> None
```
Sets up the matplotlib figure and axes for visualization.

```python
def record_session(self, score: int, session: GameSession) -> None
```
Records statistics from a completed game session.

```python
def update_visualizations(self) -> None
```
Updates all performance visualization graphs with current data.

```python
def save_statistics(self, filepath: str) -> None
```
Saves current statistics to a JSON file.

```python
def load_statistics(self, filepath: str) -> None
```
Loads statistics from a JSON file.

## UI Components Module

### ChessboardCanvas
Canvas widget for rendering the interactive chessboard.

#### Methods
```python
def draw_board(self, is_white_perspective: bool) -> None
```
Draws the chessboard with current perspective.

```python
def toggle_coordinates(self, is_white_perspective: bool) -> None
```
Toggles the visibility of coordinate labels.

```python
def bind_click(self, callback) -> None
```
Binds click event to canvas with provided callback.

### CoordinateDisplay
Display widget for showing the current target coordinate.

#### Methods
```python
def update_text(self, text: str) -> None
```
Updates the displayed coordinate text.

### StatisticsPanel
Panel for displaying current game statistics.

#### Methods
```python
def update_stats(self, stats: dict) -> None
```
Updates all statistics displays with current values.

### GameControls
Control panel for game settings and actions.

#### Methods
```python
def create_buttons(self, commands: dict, config: UIConfig) -> None
```
Creates and configures control buttons with specified commands.

```python
def update_timer(self, time_left: int) -> None
```
Updates the timer display.

```python
def get_duration(self) -> int
```
Returns the current slider value for game duration.

### PerformanceGraphs
Matplotlib-based performance visualization panel.

#### Methods
```python
def refresh(self) -> None
```
Refreshes the graph display.

```python
def get_figure(self) -> Figure
```
Returns the matplotlib figure object.

### UIConfig
Configuration settings for UI components.

#### Properties
```python
COLORS: Dict[str, str] = {
    'primary': '#1a365d',
    'secondary': '#2d3748',
    'white_square': '#f7fafc',
    'black_square': '#4a5568',
    'accent': '#3182ce',
    'text': '#2d3748',
    'background': '#ffffff'
}

FONTS: Dict[str, Tuple] = {
    'header': ('Helvetica', 14, 'bold'),
    'subheader': ('Helvetica', 12, 'bold'),
    'normal': ('Helvetica', 10),
    'coordinate': ('Helvetica', 24, 'bold')
}

GRID_SIZE: int = 8
TILE_SIZE: int = 60
```

## Usage Examples

### Creating a New Game Session
```python
game_state = GameState()
game_state.start_game()

# Generate new coordinate
coordinate, col, row = game_state.board.generate_coordinate()

# Handle click
is_correct = game_state.board.validate_click(click_x, click_y)
if is_correct:
    response_time = time.time() - last_coordinate_time
    game_state.performance.record_attempt(True, response_time)
```

### Managing Statistics
```python
tracker = PerformanceTracker()

# Record session
session = GameSession()
session.record_attempt(True, 1.0)
tracker.record_session(100, session)

# Save statistics
tracker.save_statistics("stats.json")

# Load statistics
tracker.load_statistics("stats.json")
```

### Creating UI Components
```python
config = UIConfig()

# Create chessboard
board = ChessboardCanvas(parent_widget, config)
board.bind_click(handle_click_callback)

# Create controls
controls = GameControls(parent_widget, config)
controls.create_buttons({
    'start': start_game,
    'flip': flip_board,
    'exit': exit_application
}, config)
```

## Error Handling
All methods that interact with files or external resources include proper error handling:

```python
try:
    tracker.load_statistics(filepath)
except ValueError as e:
    # Handle invalid file format
    print(f"Invalid file format: {e}")
except IOError as e:
    # Handle file access errors
    print(f"File access error: {e}")
```

## Type Hints
The codebase uses type hints throughout for better code clarity and IDE support:

```python
from typing import Dict, List, Optional, Tuple, Union

def record_attempt(self, correct: bool, response_time: float) -> None: ...
def get_session_stats(self) -> Dict[str, Union[int, float]]: ...
def generate_coordinate(self) -> Tuple[str, int, int]: ...
```

## Testing
Each component includes corresponding unit tests in the `tests/` directory. Run tests using:

```bash
python -m unittest tests/test_game_logic.py
python -m unittest tests/test_components.py
python -m unittest tests/test_integration.py
```