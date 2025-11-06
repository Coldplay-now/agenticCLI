```python
"""
终端图形界面显示模块
使用 curses 库实现贪吃蛇游戏的终端界面
"""

import curses
import time
from typing import Tuple, List
from .game import GameState, Direction


class Display:
    """终端显示控制器"""
    
    def __init__(self):
        self.screen = None
        self.game_window = None
        self.info_window = None
        self.game_width = 0
        self.game_height = 0
        
    def initialize(self, stdscr):
        """初始化 curses 显示"""
        self.screen = stdscr
        
        # 初始化颜色
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 蛇身
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # 食物
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 墙壁
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 信息
        
        # 设置键盘输入
        self.screen.keypad(True)
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        
        # 创建游戏窗口和信息窗口
        screen_height, screen_width = self.screen.getmaxyx()
        self.game_height = screen_height - 4
        self.game_width = min(screen_width - 4, 40)
        
        # 游戏主窗口
        win_y = (screen_height - self.game_height) // 2
        win_x = (screen_width - self.game_width) // 2
        self.game_window = curses.newwin(self.game_height, self.game_width, win_y, win_x)
        self.game_window.keypad(True)
        
        # 信息窗口
        self.info_window = curses.newwin(3, screen_width - 4, 1, 2)
        
        return self.game_width, self.game_height - 2
    
    def cleanup(self):
        """清理 curses 设置"""
        if self.screen:
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()
    
    def render_game(self, game_state: GameState):
        """渲染游戏画面"""
        if not self.game_window:
            return
            
        self.game_window.clear()
        self.game_window.border()
        
        # 绘制蛇
        for i, (x, y) in enumerate(game_state.snake):
            if 0 <= x < self.game_width - 2 and 0 <= y < self.game_height - 2:
                char = 'O' if i == 0 else 'o'  # 蛇头用 O，蛇身用 o
                self.game_window.addch(y + 1, x + 1, char, curses.color_pair(1))
        
        # 绘制食物
        food_x, food_y = game_state.food
        if 0 <= food_x < self.game_width - 2 and 0 <= food_y < self.game_height - 2:
            self.game_window.addch(food_y + 1, food_x + 1, '@', curses.color_pair(2))
        
        # 绘制墙壁（边界）
        for x in range(self.game_width - 2):
            self.game_window.addch(0, x + 1, '-', curses.color_pair(3))
            self.game_window.addch(self.game_height - 1, x + 1, '-', curses.color_pair(3))
        
        for y in range(self.game_height - 2):
            self.game_window.addch(y + 1, 0, '|', curses.color_pair(3))
            self.game_window.addch(y + 1, self.game_width - 1, '|', curses.color_pair(3))
        
        self.game_window.refresh()
    
    def render_info(self, game_state: GameState):
        """渲染分数和状态信息"""
        if not self.info_window:
            return
            
        self.info_window.clear()
        self.info_window.border()
        
        info_text = f" 分数: {game_state.score} | 长度: {len(game_state.snake)} | 按 'q' 退出游戏 "
        self.info_window.addstr(1, 2, info_text, curses.color_pair(4))
        
        self.info_window.refresh()
    
    def get_input(self) -> Optional[Direction]:
        """获取键盘输入"""
        if not self.game_window:
            return None
            
        self.game_window.timeout(100)  # 非阻塞输入，100ms 超时
        
        try:
            key = self.game_window.getch()
            
            if key == curses.KEY_UP or key == ord('w'):
                return Direction.UP
            elif key == curses.KEY_DOWN or key == ord('s'):
                return Direction.DOWN
            elif key == curses.KEY_LEFT or key == ord('a'):
                return Direction.LEFT
            elif key == curses.KEY_RIGHT or key == ord('d'):
                return Direction.RIGHT
            elif key == ord('q'):
                return 'QUIT'
            else:
                return None
                
        except curses.error:
            return None
    
    def show_start_screen(self):
        """显示开始界面"""
        if not self.screen:
            return
            
        self.screen.clear()
        height, width = self.screen.getmaxyx()
        
        title = "贪吃蛇游戏"
        instructions = [
            "使用方向键或 WASD 控制蛇的移动",
            "吃到食物 (@) 可以增加长度和分数",
            "撞到墙壁或自己的身体游戏结束",
            "按任意键开始游戏，按 'q' 退出"
        ]
        
        # 显示标题
        self.screen.addstr(height // 2 - 4, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # 显示说明
        for i, line in enumerate(instructions):
            self.screen.addstr(height // 2 + i, (width - len(line)) // 2, line)
        
        self.screen.refresh()
        self.screen.getch()  # 等待任意按键
    
    def show_game_over(self, score: int):
        """显示游戏结束界面"""
        if not self.screen:
            return
            
        self.screen.clear()
        height, width = self.screen.getmaxyx()
        
        game_over_text = "游戏结束!"
        score_text = f"最终分数: {score}"
        restart_text = "按任意键重新开始，按 'q' 退出"
        
        self.screen.addstr(height // 2 - 1, (width - len(game_over_text)) // 2, game_over_text, curses.A_BOLD)
        self.screen.addstr(height // 2, (width - len(score_text)) // 2, score_text)
        self.screen.addstr(height // 2 + 2, (width - len(restart_text)) // 2, restart_text)
        
        self.screen.refresh()
        
        key = self.screen.getch()
        return key != ord('q')  # 返回是否重新开始


def main(stdscr):
    """主显示循环（用于测试）"""
    display = Display()
    game_width, game_height = display.initialize(stdscr)
    
    from .game import GameState
    game_state = GameState(game_width, game_height)
    
    display.show_start_screen()
    
    # 简单的游戏循环示例
    while not game_state.game_over:
        display.render_game(game_state)
        display.render_info(game_state)
        
        direction = display.get_input()
        if direction == 'QUIT':
            break
        elif direction:
            game_state.change_direction(direction)
        
        game_state.update()
        time.sleep(0.1)
    
    if game_state.game_over:
        display.show_game_over(game_state.score)
    
    display.cleanup()


if __name__ == "__main__":
    curses.wrapper(main)
```