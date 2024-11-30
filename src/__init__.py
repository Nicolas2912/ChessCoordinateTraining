# src/__init__.py

"""
Chess Coordinates Training Application

A comprehensive training tool for improving chess coordinate recognition,
featuring interactive exercises, performance tracking, and statistical analysis.
"""

__version__ = '0.1'
__author__ = 'Nicolas'

from .core.game_logic import ChessBoardState, GameState
from .core.stats import GameSession, PerformanceTracker
from .ui.components import ChessboardCanvas, GameControls, PerformanceGraphs

__all__ = [
    'ChessBoardState',
    'GameState',
    'GameSession',
    'PerformanceTracker',
    'ChessboardCanvas',
    'GameControls',
    'PerformanceGraphs'
]