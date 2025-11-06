#!/usr/bin/env python3
import curses
from .game import SnakeGame

def main():
    try:
        curses.wrapper(start_game)
    except KeyboardInterrupt:
        print("\nGame interrupted by user")

def start_game(stdscr):
    # 初始化游戏
    game = SnakeGame(stdscr)
    
    # 显示欢迎信息
    stdscr.clear()
    stdscr.addstr(5, 10, "Welcome to Snake Game!")
    stdscr.addstr(7, 10, "Use arrow keys to control the snake")
    stdscr.addstr(8, 10, "Press 'q' to quit the game")
    stdscr.addstr(10, 10, "Press any key to start...")
    stdscr.refresh()
    stdscr.getch()
    
    # 开始游戏
    game.run()

if __name__ == "__main__":
    main()