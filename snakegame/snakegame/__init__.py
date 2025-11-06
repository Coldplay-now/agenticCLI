"""
Snake Game - A simple terminal-based snake game
"""

__version__ = "1.0.0"
__author__ = "Snake Game Developer"

from .game import SnakeGame
from .cli import main

__all__ = ['SnakeGame', 'main']