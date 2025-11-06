import curses
import random
import time
from enum import Enum, auto
from typing import List, Tuple, Optional


class EnemyType(Enum):
    GOOMBA = auto()      # 蘑菇怪
    KOOPA = auto()       # 乌龟
    PIRANHA = auto()     # 食人花


class ItemType(Enum):
    COIN = auto()
    MUSHROOM = auto()
    FLOWER = auto()
    STAR = auto()


class Enemy:
    def __init__(self, x: int, y: int, enemy_type: EnemyType):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = -1  # -1: left, 1: right
        self.is_alive = True
        self.is_shell = False  # 乌龟壳状态
        self.shell_timer = 0
        self.width = 2
        self.height = 1
        
        # 根据敌人类型设置属性
        if enemy_type == EnemyType.GOOMBA:
            self.speed = 0.5
            self.health = 1
            self.points = 100
        elif enemy_type == EnemyType.KOOPA:
            self.speed = 0.4
            self.health = 2
            self.points = 200
        elif enemy_type == EnemyType.PIRANHA:
            self.speed = 0
            self.health = 1
            self.points = 300
            self.emerging = False
            self.emerging_timer = 0

    def update(self, platforms: List, player_x: int, player_y: int, screen_width: int) -> None:
        """更新敌人状态和位置"""
        if not self.is_alive:
            return
            
        # 应用重力（除了食人花）
        if self.enemy_type != EnemyType.PIRANHA:
            self.velocity_y += 0.1
        
        # 敌人类型特定的AI行为
        if self.enemy_type == EnemyType.GOOMBA:
            self._update_goomba(platforms, screen_width)
        elif self.enemy_type == EnemyType.KOOPA:
            self._update_koopa(platforms, screen_width)
        elif self.enemy_type == EnemyType.PIRANHA:
            self._update_piranha(player_x, player_y)
        
        # 更新位置
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        # 检查平台碰撞
        self._check_platform_collision(platforms, new_x, new_y)
        
        # 边界检查
        if new_x < 0:
            new_x = 0
            self.direction = 1
        elif new_x > screen_width - self.width:
            new_x = screen_width - self.width
            self.direction = -1
            
        self.x = new_x
        self.y = new_y

    def _update_goomba(self, platforms: List, screen_width: int) -> None:
        """蘑菇怪的AI行为"""
        if not self.is_shell:
            self.velocity_x = self.speed * self.direction
            
        # 简单的边缘检测
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y <= platform.y and
                ((self.x + self.width <= platform.x and self.direction == 1) or
                 (self.x >= platform.x + platform.width and self.direction == -1))):
                self.direction *= -1
                break

    def _update_koopa(self, platforms: List, screen_width: int) -> None:
        """乌龟的AI行为"""
        if self.is_shell:
            self.shell_timer -= 1
            if self.shell_timer <= 0:
                self.is_shell = False
                self.health = 2
                self.speed = 0.4
        else:
            self.velocity_x = self.speed * self.direction
            
        # 边缘检测
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y <= platform.y and
                ((self.x + self.width <= platform.x and self.direction == 1) or
                 (self.x >= platform.x + platform.width and self.direction == -1))):
                self.direction *= -1
                break

    def _update_piranha(self, player_x: int, player_y: int) -> None:
        """食人花的AI行为"""
        self.emerging_timer += 1
        
        # 每3秒切换一次状态
        if self.emerging_timer >= 180:  # 3秒 * 60帧
            self.emerging = not self.emerging
            self.emerging_timer = 0
            
        # 如果玩家靠近，保持隐藏
        player_distance = abs(player_x - self.x)
        if player_distance < 20:
            self.emerging = False
            self.emerging_timer = 0

    def _check_platform_collision(self, platforms: List, new_x: float, new_y: float) -> None:
        """检查与平台的碰撞"""
        on_ground = False
        
        for platform in platforms:
            # 水平碰撞检查
            if (new_y + self.height > platform.y and 
                new_y < platform.y + 1 and
                new_x + self.width > platform.x and 
                new_x < platform.x + platform.width):
                
                # 从上方碰撞
                if self.y + self.height <= platform.y:
                    new_y = platform.y - self.height
                    self.velocity_y = 0
                    on_ground = True
                
                # 从侧面碰撞
                elif (self.x + self.width <= platform.x or 
                      self.x >= platform.x + platform.width):
                    self.direction *= -1
                    new_x = self.x
            
            self.x = new_x
            self.y = new_y

    def take_damage(self, from_above: bool = False) -> bool:
        """敌人受到伤害"""
        if self.enemy_type == EnemyType.KOOPA and self.health == 2 and from_above:
            # 乌龟被踩变成龟壳
            self.health = 1
            self.is_shell = True
            self.shell_timer = 300  # 5秒后恢复
            self.speed = 0
            return True
        elif from_above:
            # 被踩死
            self.is_alive = False
            return True
        else:
            # 被其他方式攻击
            self.health -= 1
            if self.health <= 0:
                self.is_alive = False
                return True
        return False

    def draw(self, stdscr) -> None:
        """绘制敌人"""
        if not self.is_alive:
            return
            
        if self.enemy_type == EnemyType.PIRANHA and not self.emerging:
            return
            
        char = 'M'  # 蘑菇怪
        if self.enemy_type == EnemyType.KOOPA:
            char = 'T' if not self.is_shell else 'S'  # 乌龟 / 龟壳
        elif self.enemy_type == EnemyType.PIRANHA:
            char = 'P'
            
        try:
            stdscr.addch(int(self.y), int(self.x), char)
            if self.width > 1:
                stdscr.addch(int(self.y), int(self.x) + 1, char)
        except curses.error:
            pass


class Item:
    def __init__(self, x: int, y: int, item_type: ItemType):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.velocity_y = 0
        self.is_collected = False
        self.bounce_timer = 0
        self.width = 1
        self.height = 1
        
        # 物品效果
        if item_type == ItemType.COIN:
            self.points = 100
        elif item_type == ItemType.MUSHROOM:
            self.points = 1000
        elif item_type == ItemType.FLOWER:
            self.points = 1000
        elif item_type == ItemType.STAR:
            self.points = 1000

    def update(self, platforms: List) -> None:
        """更新物品状态"""
        if self.is_collected:
            return
            
        # 应用重力（除了金币）
        if self.item_type != ItemType.COIN:
            self.velocity_y += 0.1
            
        # 更新位置
        new_x = self.x
        new_y = self.y + self.velocity_y
        
        # 检查平台碰撞
        on_ground = False
        for platform in platforms:
            if (new_y + self.height >= platform.y and 
                self.y + self.height <= platform.y and
                new_x + self.width > platform.x and 
                new_x < platform.x + platform.width):
                new_y = platform.y - self.height
                self.velocity_y = 0
                on_ground = True
                break
                
        self.y = new_y
        
        # 金币弹跳动画
        if self.item_type == ItemType.COIN:
            self.bounce_timer += 1
            if self.bounce_timer < 30:  # 上升阶段
                self.y -= 0.5
            elif self.bounce_timer < 60:  # 下降阶段
                self.y += 0.5
            else:
                self.is_collected = True

    def collect(self) -> Tuple[int, Optional[str]]:
        """收集物品"""
        self.is_collected = True
        
        power_up = None
        if self.item_type == ItemType.MUSHROOM:
            power_up = "super"
        elif self.item_type == ItemType.FLOWER:
            power_up = "fire"
        elif self.item_type == ItemType.STAR:
            power_up = "invincible"
            
        return self.points, power_up

    def draw(self, stdscr) -> None:
        """绘制物品"""
        if self.is_collected:
            return
            
        char = 'C'  # 金币
        if self.item_type == ItemType.MUSHROOM:
            char = 'U'  # 蘑菇
        elif self.item_type == ItemType.FLOWER:
            char = 'F'  # 花
        elif self.item_type == ItemType.STAR:
            char = '*'  # 星星
            
        try:
            stdscr.addch(int(self.y), int(self.x), char)
        except curses.error:
            pass


class EnemyManager:
    def __init__(self):
        self.enemies: List[Enemy] = []
        self.items: List[Item] = []
        
    def spawn_enemy(self, x: int, y: int, enemy_type: EnemyType) -> None:
        """生成敌人"""
        enemy = Enemy(x, y, enemy_type)
        self.enemies.append(enemy)
        
    def spawn_item(self, x: int, y: int, item_type: ItemType) -> None:
        """生成物品"""
        item = Item(x, y, item_type)
        self.items.append(item)
        
    def update_all(self, platforms: List, player_x: int, player_y: int, screen_width: int) -> None:
        """更新所有敌人和物品"""
        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(platforms, player_x, player_y, screen_width)
            if not enemy.is_alive:
                self.enemies.remove(enemy)
                
        # 更新物品
        for item in self.items[:]:
            item.update(platforms)
            if item.is_collected:
                self.items.remove(item)
                
    def check_player_collision(self, player_x: int, player_y: int, player_width: int, 
                             player_height: int, player_invincible: bool) -> Tuple[bool, int]:
        """检查玩家与敌人的碰撞"""
        points_earned = 0
        player_hit = False
        
        for enemy in self.enemies[:]:
            if not enemy.is_alive:
                continue
                
            # 碰撞检测
            if (player_x < enemy.x + enemy.width and
                player_x + player_width > enemy.x and
                player_y < enemy.y + enemy.height and
                player_y + player_height > enemy.y):
                
                if player_invincible:
                    # 无敌状态下直接消灭敌人
                    enemy.is_alive = False
                    points_earned += enemy.points
                elif player_y + player_height <= enemy.y + 2:  # 从上方踩
                    # 玩家踩到敌人
                    if enemy.take_damage(from_above=True):
                        points_earned += enemy.points
                else:
                    # 玩家被敌人碰到
                    player_hit = True
                    
        return player_hit, points_earned
        
    def check_item_collision(self, player_x: int, player_y: int, player_width: int, 
                           player_height: int) -> Tuple[int, Optional[str]]:
        """检查玩家与物品的碰撞"""
        total_points = 0
        power_up = None
        
        for item in self.items[:]:
            if (player_x < item.x + item.width and
                player_x + player_width > item.x and
                player_y < item.y + item.height and
                player_y + player_height > item.y):
                
                item_points, item_power_up = item.collect()
                total_points += item_points
                if item_power_up:
                    power_up = item_power_up
                    
        return total_points, power_up
        
    def draw_all(self, stdscr) -> None:
        """绘制所有敌人和物品"""
        for enemy in self.enemies:
            enemy.draw(stdscr)
            
        for item in self.items:
            item.draw(stdscr)
            
    def clear_all(self) -> None:
        """清除所有敌人和物品"""
        self.enemies.clear()
        self.items.clear()


def generate_enemies_for_level(level: int, enemy_manager: EnemyManager) -> None:
    """根据关卡生成敌人"""
    enemy_manager.clear_all()
    
    if level == 1:
        # 第一关：简单的蘑菇怪
        enemy_manager.spawn_enemy(20, 18, EnemyType.GOOMBA)
        enemy_manager.spawn_enemy(40, 18, EnemyType.GOOMBA)
        enemy_manager.spawn_enemy(60, 18, EnemyType.GOOMBA)
        
        # 一些金币
        enemy_manager.spawn_item(15, 15, ItemType.COIN)
        enemy_manager.spawn_item(25, 15, ItemType.COIN)
        enemy_manager.spawn_item(35, 15, ItemType.COIN)
        
    elif level == 2:
        # 第二关：混合敌人
        enemy_manager.spawn_enemy(15, 18, EnemyType.GOOMBA)
        enemy_manager.spawn_enemy(30, 18, EnemyType.KOOPA)
        enemy_manager.spawn_enemy(50, 18, EnemyType.GOOMBA)
        enemy_manager.spawn_enemy(65, 18, EnemyType.KOOPA)
        
        # 更多物品
        enemy_manager.spawn_item(20, 15, ItemType.COIN)
        enemy_manager.spawn_item(40, 15, ItemType.MUSHROOM)
        enemy_manager.spawn_item(60, 15, ItemType.COIN)
        
    elif level == 3:
        # 第三关：挑战性敌人
        enemy_manager.spawn_enemy(10, 18, EnemyType.GOOMBA)
        enemy_manager.spawn_enemy(25, 18, EnemyType.KOOPA)
        enemy_manager.spawn_enemy(45, 18, EnemyType.PIRANHA)
        enemy_manager.spawn_enemy(60, 18, EnemyType.KOOPA)
        enemy_manager.spawn_enemy(75, 18, EnemyType.GOOMBA)
        
        # 强力物品
        enemy_manager.spawn_item(35, 15, ItemType.FLOWER)
        enemy_manager.spawn_item(55, 15, ItemType.STAR)
        enemy_manager.spawn_item(15, 12, ItemType.COIN)
