"""
贪吃蛇游戏核心逻辑模块
"""

import random
import time
from enum import Enum
from typing import List, Tuple, Optional


class Direction(Enum):
    """移动方向枚举"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameState:
    """游戏状态管理类"""
    
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.score = 0
        self.game_over = False
        self.snake: List[Tuple[int, int]] = [(width // 2, height // 2)]
        self.direction = Direction.RIGHT
        self.food = self._generate_food()
        self.speed = 0.2  # 初始速度（秒）
    
    def _generate_food(self) -> Tuple[int, int]:
        """随机生成食物位置"""
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food
    
    def change_direction(self, new_direction: Direction):
        """改变蛇的移动方向"""
        # 防止直接反向移动
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction
    
    def move_snake(self):
        """移动蛇"""
        if self.game_over:
            return
        
        # 计算新的头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # 碰撞检测
        if self._check_collision(new_head):
            self.game_over = True
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self._generate_food()
            # 随着分数增加，速度加快
            self.speed = max(0.05, self.speed - 0.01)
        else:
            # 如果没有吃到食物，移除尾部
            self.snake.pop()
    
    def _check_collision(self, position: Tuple[int, int]) -> bool:
        """碰撞检测"""
        x, y = position
        
        # 墙壁碰撞
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        # 自身碰撞
        if position in self.snake:
            return True
        
        return False
    
    def get_game_info(self) -> dict:
        """获取游戏信息"""
        return {
            'score': self.score,
            'snake_length': len(self.snake),
            'game_over': self.game_over,
            'food_position': self.food,
            'snake_body': self.snake.copy()
        }


class SnakeGame:
    """贪吃蛇游戏主类"""
    
    def __init__(self, width: int = 20, height: int = 20):
        self.state = GameState(width, height)
    
    def handle_input(self, key: str) -> bool:
        """处理键盘输入"""
        direction_map = {
            'w': Direction.UP,
            's': Direction.DOWN,
            'a': Direction.LEFT,
            'd': Direction.RIGHT,
            'up': Direction.UP,
            'down': Direction.DOWN,
            'left': Direction.LEFT,
            'right': Direction.RIGHT
        }
        
        if key in direction_map:
            self.state.change_direction(direction_map[key])
            return True
        return False
    
    def update(self):
        """更新游戏状态"""
        self.state.move_snake()
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.state.game_over
    
    def get_score(self) -> int:
        """获取当前分数"""
        return self.state.score
    
    def get_game_state(self) -> dict:
        """获取游戏状态信息"""
        return self.state.get_game_info()
    
    def reset(self):
        """重置游戏"""
        self.state = GameState(self.state.width, self.state.height)


def create_game(width: int = 20, height: int = 20) -> SnakeGame:
    """创建新的游戏实例"""
    return SnakeGame(width, height)


def main_game_loop():
    """主游戏循环（用于测试）"""
    game = create_game()
    
    print("贪吃蛇游戏开始！")
    print("使用 WASD 键控制方向")
    print("按 Ctrl+C 退出游戏")
    
    try:
        while not game.is_game_over():
            # 清屏（简化版）
            print("\n" * 50)
            
            # 显示游戏状态
            state = game.get_game_state()
            print(f"分数: {state['score']} | 蛇长度: {state['snake_length']}")
            print(f"食物位置: {state['food_position']}")
            
            # 这里可以添加图形显示逻辑
            # 简化显示：只显示坐标信息
            print(f"蛇身: {state['snake_body'][:3]}...")  # 只显示前3个坐标
            
            # 模拟输入（实际游戏中应该从键盘获取）
            # 这里使用随机方向进行演示
            directions = ['w', 's', 'a', 'd']
            game.handle_input(random.choice(directions))
            
            game.update()
            time.sleep(game.state.speed)
        
        print(f"\n游戏结束！最终分数: {game.get_score()}")
        
    except KeyboardInterrupt:
        print("\n游戏被用户中断")


if __name__ == "__main__":
    main_game_loop()