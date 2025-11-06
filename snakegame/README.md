# Snake Game

A simple terminal-based snake game built with Python and curses.

## Features

- Classic snake gameplay
- Score tracking
- Terminal-based interface
- No external dependencies

## Installation

Clone the repository and run the game:

```bash
git clone <repository-url>
cd snakegame
python -m snakegame.cli
```

## How to Play

1. Use arrow keys to control the snake
2. Eat the food (*) to grow and increase your score
3. Avoid hitting the walls or yourself
4. Press 'q' to quit the game

## Requirements

- Python 3.6+
- Unix-like system (for curses support)

## Development

This project uses only Python standard library modules:
- `curses` for terminal UI
- `random` for food generation
- `time` for game timing