import curses
import time
import random
from enum import Enum, auto


class GameState(Enum):
    START = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class Player:
    def __init__(self, x, y):
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

    def move(self, direction):
        if direction == Direction.LEFT:
            self.velocity_x = -1
            self.direction = Direction.LEFT
        elif direction == Direction.RIGHT:
            self.velocity_x = 1
            self.direction = Direction.RIGHT
        elif direction == Direction.UP and not self.is_jumping:
            self.velocity_y = -2
            self.is_jumping = True

    def update(self, platforms):
        # 应用重力
        self.velocity_y += 0.1
        
        # 更新位置
        new_x = self.x + self.velocity_x
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
                self.is_jumping = False
                on_ground = True
                break
        
        # 边界检查
        if new_x < 0:
            new_x = 0
        if new_x > 77:  # 屏幕宽度 - 玩家宽度
            new_x = 77
        
        self.x = new_x
        self.y = new_y
        
        # 重置水平速度
        self.velocity_x = 0


class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = -0.5
        self.width = 2
        self.height = 1

    def update(self, platforms):
        self.x += self.velocity_x
        
        # 简单的AI：在平台边缘转向
        on_platform = False
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 1 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                on_platform = True
                # 检查是否到达平台边缘
                if (self.x <= platform.x and self.velocity_x < 0) or \
                   (self.x + self.width >= platform.x + platform.width and self.velocity_x > 0):
                    self.velocity_x *= -1
                break
        
        if not on_platform:
            self.velocity_x *= -1


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.state = GameState.START
        self.player = Player(5, 10)
        self.platforms = []
        self.enemies = []
        self.frame_count = 0
        self.level = 1
        self.setup_level()
        
        # 初始化curses
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)  # 20 FPS

    def setup_level(self):
        self.platforms = [
            Platform(0, 15, 80),  # 地面
            Platform(10, 12, 5),
            Platform(20, 10, 5),
            Platform(30, 8, 5),
            Platform(40, 10, 5),
            Platform(50, 12, 5),
            Platform(60, 8, 10),  # 终点平台
        ]
        
        self.enemies = [
            Enemy(15, 14),
            Enemy(25, 9),
            Enemy(45, 9),
        ]
        
        self.player.x = 5
        self.player.y = 10

    def handle_input(self):
        try:
            key = self.stdscr.getch()
            
            if self.state == GameState.START:
                if key == ord(' '):
                    self.state = GameState.PLAYING
                elif key == ord('q'):
                    return False
            
            elif self.state == GameState.PLAYING:
                if key == curses.KEY_LEFT:
                    self.player.move(Direction.LEFT)
                elif key == curses.KEY_RIGHT:
                    self.player.move(Direction.RIGHT)
                elif key == curses.KEY_UP:
                    self.player.move(Direction.UP)
                elif key == ord('q'):
                    return False
            
            elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                if key == ord(' '):
                    self.__init__(self.stdscr)
                elif key == ord('q'):
                    return False
            
            return True
        except:
            return True

    def update(self):
        if self.state != GameState.PLAYING:
            return

        self.frame_count += 1
        
        # 更新玩家
        self.player.update(self.platforms)
        
        # 更新敌人
        for enemy in self.enemies:
            enemy.update(self.platforms)
        
        # 检查敌人碰撞
        for enemy in self.enemies[:]:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                
                # 如果玩家从上方跳在敌人头上
                if self.player.velocity_y > 0 and self.player.y + self.player.height <= enemy.y + 2:
                    self.enemies.remove(enemy)
                    self.player.score += 100
                    self.player.velocity_y = -1  # 反弹
                else:
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
                    else:
                        # 重置玩家位置
                        self.player.x = 5
                        self.player.y = 10
                        self.player.velocity_x = 0
                        self.player.velocity_y = 0
        
        # 检查是否到达终点
        if (self.player.x >= 60 and self.player.x <= 70 and
            self.player.y <= 8 and self.player.y >= 6):
            self.state = GameState.VICTORY
            self.player.score += 1000

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        if self.state == GameState.START:
            title = "超级玛丽 - 命令行版"
            instructions = "按空格键开始游戏，按Q退出"
            controls = "方向键移动，空格键跳跃"
            
            self.stdscr.addstr(height//2 - 2, (width - len(title))//2, title)
            self.stdscr.addstr(height//2, (width - len(instructions))//2, instructions)
            self.stdscr.addstr(height//2 + 1, (width - len(controls))//2, controls)
        
        elif self.state == GameState.PLAYING:
            # 绘制平台
            for platform in self.platforms:
                for i in range(platform.width):
                    self.stdscr.addch(platform.y, platform.x + i, '=')
            
            # 绘制敌人
            for enemy in self.enemies:
                self.stdscr.addch(enemy.y, enemy.x, 'G')
            
            # 绘制玩家
            player_char = '<' if self.player.direction == Direction.LEFT else '>'
            self.stdscr.addch(int(self.player.y), int(self.player.x), player_char)
            self.stdscr.addch(int(self.player.y) + 1, int(self.player.x), 'M')
            
            # 绘制UI
            self.stdscr.addstr(0, 0, f"分数: {self.player.score}")
            self.stdscr.addstr(0, 20, f"生命: {self.player.lives}")
            self.stdscr.addstr(0, 40, f"关卡: {self.level}")
        
        elif self.state == GameState.GAME_OVER:
            message = "游戏结束!"
            score = f"最终分数: {self.player.score}"
            restart = "按空格键重新开始，按Q退出"
            
            self.stdscr.addstr(height//2 - 1, (width - len(message))//2, message)
            self.stdscr.addstr(height//2, (width - len(score))//2, score)
            self.stdscr.addstr(height//2 + 1, (width - len(restart))//2, restart)
        
        elif self.state == GameState.VICTORY:
            message = "恭喜通关!"
            score = f"最终分数: {self.player.score}"
            restart = "按空格键重新开始，按Q退出"
            
            self.stdscr.addstr(height//2 - 1, (width - len(message))//2, message)
            self.stdscr.addstr(height//2, (width - len(score))//2, score)
            self.stdscr.addstr(height//2 + 1, (width - len(restart))//2, restart)
        
        self.stdscr.refresh()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            time.sleep(0.05)  # 控制帧率


def main_game_loop():
    """主游戏循环"""
    def wrapper(stdscr):
        game = Game(stdscr)
        game.run()
    
    curses.wrapper(wrapper)
    return "游戏结束"


# 用于测试的简单版本（不使用curses）
def simple_game_loop():
    """简单版本的游戏循环（用于测试）"""
    print("超级玛丽游戏启动中...")
    print("使用方向键移动，空格键跳跃")
    print("按Q退出游戏")
    return "游戏执行完成"
