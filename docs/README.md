# Chess Coordinates Trainer 🎯

An advanced, interactive chess coordinates training application designed with a focus on precise timing, statistical analysis, and performance tracking. Built using Python and Tkinter, this application combines mathematical rigor with an intuitive user interface to help players master chess board coordinates.

![UI_example_v01](https://github.com/user-attachments/assets/3b359bc4-4faf-4b90-b29e-42e71dce7f03)

## Table of Contents
- [Core Features](#core-features)
- [Technical Architecture](#technical-architecture)
- [Mathematical Components](#mathematical-components)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Performance Analytics](#performance-analytics)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Contributing](#contributing)

## Core Features

### 🎮 Interactive Training Interface
- Dynamic 8x8 chessboard with configurable perspectives
- Real-time coordinate validation
- Adaptive color schemes for optimal visibility
- Toggle-able coordinate overlay system

### 📊 Performance Analytics
- Comprehensive statistical tracking
- Real-time performance metrics
- Historical trend analysis
- Visual performance graphs using Matplotlib

### ⚙️ Customization Options
- Configurable practice session duration (5-60 seconds)
- Board perspective switching (White/Black)
- Coordinate visibility toggling
- Custom color schemes

### 💾 Data Management
- JSON-based statistics persistence
- Session history tracking
- Performance data export/import
- Timestamped records

## Technical Architecture

### Component Structure
```
ChessCoordinateTraining/
├── src/
│   ├── core/
│   │   ├── game_logic.py      # Core game mechanics
│   │   └── stats.py           # Statistical analysis
│   └── ui/
│       └── components.py      # UI components
├── tests/
│   ├── test_components.py     # UI testing
│   ├── test_game_logic.py     # Core logic testing
│   └── test_integration.py    # Integration testing
└── main.py                    # Application entry point
```

### Key Classes
1. `ChessCoordinatesGame`: Main application controller
2. `GameState`: Game state management
3. `PerformanceTracker`: Statistical analysis engine
4. `ChessboardCanvas`: Visual board representation

## Mathematical Components

### Scoring System
The application employs a sophisticated scoring algorithm:

```python
score = base_score + accuracy_bonus + speed_bonus - penalties

where:
- base_score = correct_clicks * 100
- accuracy_bonus = base_score * (correct_clicks / total_clicks)
- speed_bonus = max(0, 500 - (avg_response_time * 100))
- penalties = wrong_clicks * 50
```

### Performance Metrics
- Accuracy Calculation: `accuracy = (correct_clicks / total_clicks) * 100`
- Response Time Analysis: `avg_response_time = total_response_time / correct_clicks`
- Statistical Trend Analysis using moving averages

## Installation

### Prerequisites
- Python 3.8+
- Required packages:
  ```bash
  pip install -r requirements.txt
  ```

### Setup
```bash
git clone https://github.com/yourusername/chess-coordinates-trainer.git
cd chess-coordinates-trainer
python -m pip install -e .
```

## Usage Guide

### Basic Usage
1. Start the application:
   ```bash
   python main.py
   ```
2. Configure session duration using the slider
3. Click "Start" to begin training
4. Click the corresponding square when shown a coordinate

### Advanced Features
- **Board Flipping**: Use "Flip Board" for perspective training
- **Statistics Export**: Save your progress via "Save Stats"
- **Data Analysis**: View performance trends in the graphs panel
- **Session Management**: Load/unload previous training data

## Performance Analytics

### Tracked Metrics
1. **Accuracy Metrics**
   - Correct/incorrect moves
   - Success rate percentage
   - Moving accuracy average

2. **Timing Metrics**
   - Average response time
   - Fastest/slowest responses
   - Time-based performance trends

3. **Progress Tracking**
   - Historical performance data
   - Session-by-session comparison
   - Long-term improvement analysis

### Visualization Components
- Score progression graphs
- Accuracy trend analysis
- Response time distribution
- Click pattern analysis

## Development Guidelines

### Code Structure
- Modular architecture with clear separation of concerns
- Event-driven design for UI interactions
- Object-oriented implementation
- Comprehensive error handling

### Best Practices
1. Follow PEP 8 style guidelines
2. Maintain comprehensive docstrings
3. Implement unit tests for new features
4. Use type hints for better code clarity

## Testing

### Test Categories
1. **Unit Tests**
   ```bash
   python -m unittest tests/test_game_logic.py
   python -m unittest tests/test_components.py
   ```

2. **Integration Tests**
   ```bash
   python -m unittest tests/test_integration.py
   ```

### Coverage
- Core game logic: 95%+ coverage
- UI components: 90%+ coverage
- Integration scenarios: 85%+ coverage

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit pull request

### Code Style
- Use Black for formatting
- Maintain docstring coverage
- Follow type hinting conventions
- Keep cyclomatic complexity low

### Pull Request Process
1. Update documentation
2. Add unit tests
3. Ensure CI passes
4. Request code review

---

## Acknowledgments
- Chess coordinate training methodology
- Performance tracking algorithms
- UI/UX design principles
