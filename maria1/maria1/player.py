import curses
import time
import random
from enum import Enum, auto
from typing import List, Tuple


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = Direction.RIGHT
        self.is_jumping = False
        self.lives = 3
        self.score = 0
        self.width = 3
        self.height = 2
        self.invincible = False
        self.invincible_timer = 0
        self.power_up = None

    def move(self, direction: Direction) -> None:
        if direction == Direction.LEFT:
            self.velocity_x = -1.5
            self.direction = Direction.LEFT
        elif direction == Direction.RIGHT:
            self.velocity_x = 1.5
            self.direction = Direction.RIGHT
        elif direction == Direction.UP and not self.is_jumping:
            self.velocity_y = -3.0
            self.is_jumping = True

    def update(self, platforms: List, enemies: List, items: List, screen_width: int) -> None:
        # 应用重力
        self.velocity_y += 0.2
        
        # 更新无敌状态
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # 更新位置
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        # 检查平台碰撞
        on_ground = False
        for platform in platforms:
            if self._check_collision(new_x, new_y, platform):
                # 从上方碰撞平台
                if (self.y + self.height <= platform.y and 
                    new_y + self.height >= platform.y):
                    new_y = platform.y - self.height
                    self.velocity_y = 0
                    self.is_jumping = False
                    on_ground = True
                # 从下方碰撞平台
                elif (self.y >= platform.y + 1 and 
                      new_y <= platform.y + 1):
                    new_y = platform.y + 1
                    self.velocity_y = 0
                # 水平碰撞
                elif (new_x + self.width > platform.x and 
                      new_x < platform.x + platform.width):
                    if self.velocity_x > 0:  # 向右移动
                        new_x = platform.x - self.width
                    elif self.velocity_x < 0:  # 向左移动
                        new_x = platform.x + platform.width
                    self.velocity_x = 0
        
        # 检查敌人碰撞
        if not self.invincible:
            for enemy in enemies:
                if self._check_collision(new_x, new_y, enemy):
                    # 从上方踩敌人
                    if (self.y + self.height <= enemy.y + 1 and 
                        self.velocity_y > 0):
                        enemy.alive = False
                        self.velocity_y = -1.5  # 小反弹
                        self.score += 100
                    else:
                        self.take_damage()
        
        # 检查物品碰撞
        for item in items[:]:
            if self._check_collision(new_x, new_y, item):
                self.collect_item(item)
                items.remove(item)
        
        # 边界检查
        if new_x < 0:
            new_x = 0
            self.velocity_x = 0
        if new_x > screen_width - self.width:
            new_x = screen_width - self.width
            self.velocity_x = 0
        
        # 检查掉落死亡
        if new_y > 25:  # 屏幕底部
            self.take_damage()
            new_x = 10  # 重生位置
            new_y = 10
        
        self.x = new_x
        self.y = new_y
        
        # 重置水平速度（如果没有持续输入）
        self.velocity_x *= 0.8  # 摩擦力

    def _check_collision(self, x: float, y: float, obj) -> bool:
        return (x < obj.x + obj.width and
                x + self.width > obj.x and
                y < obj.y + obj.height and
                y + self.height > obj.y)

    def take_damage(self) -> None:
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 60  # 1秒无敌时间
            self.x = 10  # 重生位置
            self.y = 10
            self.velocity_x = 0
            self.velocity_y = 0

    def collect_item(self, item) -> None:
        if item.type == "coin":
            self.score += 200
        elif item.type == "mushroom":
            self.lives = min(self.lives + 1, 5)
            self.score += 500
        elif item.type == "flower":
            self.power_up = "fire"
            self.score += 1000

    def draw(self, stdscr) -> None:
        # 绘制玩家角色
        char = 'M' if not self.invincible or time.time() % 0.5 > 0.25 else '?'
        
        if self.direction == Direction.RIGHT:
            stdscr.addch(int(self.y), int(self.x), char)
            stdscr.addch(int(self.y), int(self.x) + 1, '>')
            stdscr.addch(int(self.y) + 1, int(self.x), '|')
            stdscr.addch(int(self.y) + 1, int(self.x) + 1, '|')
        else:
            stdscr.addch(int(self.y), int(self.x) + 1, char)
            stdscr.addch(int(self.y), int(self.x), '<')
            stdscr.addch(int(self.y) + 1, int(self.x), '|')
            stdscr.addch(int(self.y) + 1, int(self.x) + 1, '|')


class Platform:
    def __init__(self, x: int, y: int, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = 1

    def draw(self, stdscr) -> None:
        for i in range(self.width):
            stdscr.addch(self.y, self.x + i, '=')


class Enemy:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.velocity_x = -0.5
        self.width = 2
        self.height = 1
        self.alive = True

    def update(self, platforms: List) -> None:
        if not self.alive:
            return
            
        self.x += self.velocity_x
        
        # 简单的AI：在平台边缘转向
        on_platform = False
        for platform in platforms:
            if (self.y + 1 >= platform.y and 
                self.y <= platform.y and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                on_platform = True
                
                # 检查平台边缘
                if (self.velocity_x < 0 and 
                    self.x <= platform.x + 1):
                    self.velocity_x = 0.5
                elif (self.velocity_x > 0 and 
                      self.x + self.width >= platform.x + platform.width - 1):
                    self.velocity_x = -0.5
                break
        
        if not on_platform:
            self.velocity_x *= -1

    def draw(self, stdscr) -> None:
        if self.alive:
            stdscr.addch(self.y, self.x, 'G')
            stdscr.addch(self.y, self.x + 1, 'o')


class Item:
    def __init__(self, x: int, y: int, item_type: str):
        self.x = x
        self.y = y
        self.type = item_type
        self.width = 1
        self.height = 1

    def draw(self, stdscr) -> None:
        if self.type == "coin":
            stdscr.addch(self.y, self.x, 'o')
        elif self.type == "mushroom":
            stdscr.addch(self.y, self.x, 'm')
        elif self.type == "flower":
            stdscr.addch(self.y, self.x, '*')


def generate_level_1() -> Tuple[List[Platform], List[Enemy], List[Item]]:
    platforms = []
    enemies = []
    items = []
    
    # 地面
    platforms.append(Platform(0, 20, 80))
    
    # 平台
    platforms.append(Platform(10, 15, 5))
    platforms.append(Platform(20, 12, 4))
    platforms.append(Platform(30, 10, 6))
    platforms.append(Platform(45, 8, 5))
    platforms.append(Platform(55, 12, 4))
    platforms.append(Platform(65, 15, 5))
    
    # 敌人
    enemies.append(Enemy(15, 14))
    enemies.append(Enemy(35, 9))
    enemies.append(Enemy(60, 11))
    
    # 物品
    items.append(Item(12, 14, "coin"))
    items.append(Item(32, 9, "coin"))
    items.append(Item(47, 7, "mushroom"))
    items.append(Item(67, 14, "flower"))
    
    return platforms, enemies, items


def generate_level_2() -> Tuple[List[Platform], List[Enemy], List[Item]]:
    platforms = []
    enemies = []
    items = []
    
    # 地面
    platforms.append(Platform(0, 20, 80))
    
    # 更复杂的平台布局
    platforms.append(Platform(5, 16, 4))
    platforms.append(Platform(15, 13, 3))
    platforms.append(Platform(25, 10, 4))
    platforms.append(Platform(35, 13, 3))
    platforms.append(Platform(45, 16, 4))
    platforms.append(Platform(55, 13, 3))
    platforms.append(Platform(65, 10, 4))
    
    # 移动平台
    platforms.append(Platform(20, 7, 3))
    platforms.append(Platform(50, 7, 3))
    
    # 更多敌人
    enemies.append(Enemy(8, 15))
    enemies.append(Enemy(28, 9))
    enemies.append(Enemy(48, 15))
    enemies.append(Enemy(68, 9))
    
    # 更多物品
    items.append(Item(6, 15, "coin"))
    items.append(Item(16, 12, "coin"))
    items.append(Item(26, 9, "coin"))
    items.append(Item(36, 12, "coin"))
    items.append(Item(46, 15, "coin"))
    items.append(Item(56, 12, "coin"))
    items.append(Item(66, 9, "coin"))
    items.append(Item(40, 6, "mushroom"))
    items.append(Item(70, 6, "flower"))
    
    return platforms, enemies, items
