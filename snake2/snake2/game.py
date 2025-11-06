"""
贪吃蛇游戏核心逻辑模块
"""
import random
import time
from typing import List, Tuple

class SnakeGame:
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.snake = [(height // 2, width // 2)]
        self.food = self._generate_food()
        self.direction = (0, 1)  # 初始向右移动
        self.score = 0
        self.game_over = False
    
    def _generate_food(self) -> Tuple[int, int]:
        """生成食物位置"""
        while True:
            food = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            if food not in self.snake:
                return food
    
    def change_direction(self, direction: Tuple[int, int]):
        """改变蛇的移动方向"""
        # 防止直接反向移动
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def move(self):
        """移动蛇"""
        if self.game_over:
            return
        
        # 计算新的头部位置
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # 检查碰撞
        if (new_head[0] < 0 or new_head[0] >= self.height or
            new_head[1] < 0 or new_head[1] >= self.width or
            new_head in self.snake):
            self.game_over = True
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
        else:
            self.snake.pop()
    
    def get_board(self) -> List[List[str]]:
        """获取游戏板状态"""
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # 绘制蛇
        for segment in self.snake:
            board[segment[0]][segment[1]] = '#'
        
        # 绘制食物
        board[self.food[0]][self.food[1]] = '*'
        
        return board