```python
"""
贪吃蛇游戏单元测试模块
"""

import pytest
from snake3.game import GameState, Direction


class TestGameState:
    """游戏状态测试类"""
    
    def test_initial_state(self):
        """测试游戏初始状态"""
        game = GameState(width=10, height=10)
        
        assert game.width == 10
        assert game.height == 10
        assert game.score == 0
        assert game.game_over is False
        assert len(game.snake) > 0
        assert game.food is not None
        
    def test_snake_movement_up(self):
        """测试蛇向上移动"""
        game = GameState(width=10, height=10)
        initial_head = game.snake[0]
        game.direction = Direction.UP
        
        game.move_snake()
        new_head = game.snake[0]
        
        expected_position = (initial_head[0], initial_head[1] - 1)
        assert new_head == expected_position
        
    def test_snake_movement_down(self):
        """测试蛇向下移动"""
        game = GameState(width=10, height=10)
        initial_head = game.snake[0]
        game.direction = Direction.DOWN
        
        game.move_snake()
        new_head = game.snake[0]
        
        expected_position = (initial_head[0], initial_head[1] + 1)
        assert new_head == expected_position
        
    def test_snake_movement_left(self):
        """测试蛇向左移动"""
        game = GameState(width=10, height=10)
        initial_head = game.snake[0]
        game.direction = Direction.LEFT
        
        game.move_snake()
        new_head = game.snake[0]
        
        expected_position = (initial_head[0] - 1, initial_head[1])
        assert new_head == expected_position
        
    def test_snake_movement_right(self):
        """测试蛇向右移动"""
        game = GameState(width=10, height=10)
        initial_head = game.snake[0]
        game.direction = Direction.RIGHT
        
        game.move_snake()
        new_head = game.snake[0]
        
        expected_position = (initial_head[0] + 1, initial_head[1])
        assert new_head == expected_position
        
    def test_food_generation_within_bounds(self):
        """测试食物生成在边界内"""
        game = GameState(width=10, height=10)
        
        # 测试多次食物生成
        for _ in range(10):
            game.generate_food()
            food_x, food_y = game.food
            
            assert 0 <= food_x < game.width
            assert 0 <= food_y < game.height
            assert game.food not in game.snake
            
    def test_food_not_on_snake(self):
        """测试食物不会生成在蛇身上"""
        game = GameState(width=5, height=5)
        
        # 在小的游戏区域中多次测试
        for _ in range(20):
            game.generate_food()
            assert game.food not in game.snake
            
    def test_collision_with_wall(self):
        """测试墙壁碰撞检测"""
        game = GameState(width=5, height=5)
        
        # 移动到边界
        game.snake = [(0, 2)]  # 蛇头在左边界
        game.direction = Direction.LEFT
        
        game.move_snake()
        assert game.game_over is True
        
    def test_collision_with_self(self):
        """测试自身碰撞检测"""
        game = GameState(width=10, height=10)
        
        # 创建会碰撞到自身的蛇
        game.snake = [(5, 5), (5, 4), (5, 3), (4, 3), (4, 4), (4, 5)]
        game.direction = Direction.UP  # 向上移动会碰到身体
        
        game.move_snake()
        assert game.game_over is True
        
    def test_no_collision_normal_movement(self):
        """测试正常移动时无碰撞"""
        game = GameState(width=10, height=10)
        initial_game_over = game.game_over
        
        game.move_snake()
        
        # 正常移动不应该导致游戏结束
        assert game.game_over == initial_game_over
        
    def test_score_increase_on_food_eat(self):
        """测试吃到食物时分数增加"""
        game = GameState(width=10, height=10)
        initial_score = game.score
        
        # 将食物放在蛇头前方
        game.direction = Direction.RIGHT
        next_head = (game.snake[0][0] + 1, game.snake[0][1])
        game.food = next_head
        
        game.move_snake()
        
        assert game.score == initial_score + 1
        assert len(game.snake) > 1  # 蛇应该变长
        
    def test_snake_growth_on_food_eat(self):
        """测试吃到食物时蛇身变长"""
        game = GameState(width=10, height=10)
        initial_length = len(game.snake)
        
        # 将食物放在蛇头前方
        game.direction = Direction.RIGHT
        next_head = (game.snake[0][0] + 1, game.snake[0][1])
        game.food = next_head
        
        game.move_snake()
        
        assert len(game.snake) == initial_length + 1
        
    def test_no_score_change_without_food(self):
        """测试未吃到食物时分数不变"""
        game = GameState(width=10, height=10)
        initial_score = game.score
        
        # 确保食物不在蛇头前方
        game.direction = Direction.RIGHT
        next_head = (game.snake[0][0] + 1, game.snake[0][1])
        if game.food == next_head:
            game.generate_food()  # 重新生成食物
            
        game.move_snake()
        
        assert game.score == initial_score


class TestDirection:
    """方向枚举测试类"""
    
    def test_direction_values(self):
        """测试方向枚举值"""
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)
        
    def test_direction_names(self):
        """测试方向枚举名称"""
        assert Direction.UP.name == "UP"
        assert Direction.DOWN.name == "DOWN"
        assert Direction.LEFT.name == "LEFT"
        assert Direction.RIGHT.name == "RIGHT"


def test_game_reset():
    """测试游戏重置功能"""
    game = GameState(width=10, height=10)
    
    # 修改游戏状态
    game.score = 5
    game.game_over = True
    original_snake_length = len(game.snake)
    
    # 重置游戏
    game.reset()
    
    assert game.score == 0
    assert game.game_over is False
    assert len(game.snake) == original_snake_length


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```