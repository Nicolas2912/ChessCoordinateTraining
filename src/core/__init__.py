# src/core/__init__.py

"""
Core game logic and statistics handling for the Chess Coordinates Training application.
"""

from .game_logic import ChessBoardState, GameState, GameConfig
from .stats import GameSession, PerformanceTracker

__all__ = [
    'ChessBoardState',
    'GameState',
    'GameConfig',
    'GameSession',
    'PerformanceTracker'
]