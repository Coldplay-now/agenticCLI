import curses
import random
import time

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.snake = [[self.height//2, self.width//2]]
        self.food = self.generate_food()
        self.direction = curses.KEY_RIGHT
        self.score = 0
        self.game_over = False
        
    def generate_food(self):
        while True:
            food = [random.randint(1, self.height-2), random.randint(1, self.width-2)]
            if food not in self.snake:
                return food
    
    def draw(self):
        self.stdscr.clear()
        
        # 绘制边界
        self.stdscr.border(0)
        
        # 绘制蛇
        for segment in self.snake:
            self.stdscr.addch(segment[0], segment[1], '#')
        
        # 绘制食物
        self.stdscr.addch(self.food[0], self.food[1], '*')
        
        # 显示分数
        self.stdscr.addstr(0, 2, f"Score: {self.score}")
        self.stdscr.addstr(0, self.width-10, "Press 'q' to quit")
        
        self.stdscr.refresh()
    
    def move(self):
        head = self.snake[0].copy()
        
        if self.direction == curses.KEY_UP:
            head[0] -= 1
        elif self.direction == curses.KEY_DOWN:
            head[0] += 1
        elif self.direction == curses.KEY_LEFT:
            head[1] -= 1
        elif self.direction == curses.KEY_RIGHT:
            head[1] += 1
        
        # 检查碰撞
        if (head[0] in [0, self.height-1] or 
            head[1] in [0, self.width-1] or 
            head in self.snake):
            self.game_over = True
            return
        
        self.snake.insert(0, head)
        
        # 检查是否吃到食物
        if head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def run(self):
        self.stdscr.timeout(100)  # 控制游戏速度
        
        while not self.game_over:
            self.draw()
            
            # 获取用户输入
            key = self.stdscr.getch()
            
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                self.direction = key
            elif key == ord('q'):
                break
            
            self.move()
        
        if self.game_over:
            self.stdscr.addstr(self.height//2, self.width//2 - 5, "GAME OVER!")
            self.stdscr.addstr(self.height//2 + 1, self.width//2 - 8, f"Final Score: {self.score}")
            self.stdscr.refresh()
            time.sleep(2)