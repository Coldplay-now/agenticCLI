"""
snake3 - 终端贪吃蛇游戏
"""

__version__ = "0.1.0"

from .game import SnakeGame, create_game, main_game_loop

__all__ = ["SnakeGame", "create_game", "main_game_loop", "__version__"]


