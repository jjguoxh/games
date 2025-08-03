# bluetooth_tetris.py
import pygame
import random
import sys
import json
import threading
import time
from datetime import datetime

# 蓝牙通信相关导入
try:
    import bluetooth  # pybluez库

    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("蓝牙库未安装，将使用模拟模式")


# 原有的俄罗斯方块代码保持不变
# ... (此处保持您原有的所有常量和类定义) ...

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("俄罗斯方块 - 蓝牙对战版")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # 蓝牙相关属性
        self.bluetooth_manager = None
        self.opponent_score = 0
        self.opponent_lines = 0
        self.opponent_name = "对手"
        self.is_host = False
        self.game_mode = "single"  # single, host, client

        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # 秒
        self.fall_time = 0

    # ... (保持原有的所有方法不变) ...

    def draw_sidebar(self):
        sidebar_rect = pygame.Rect(
            SCREEN_WIDTH - SIDEBAR_WIDTH,
            0,
            SIDEBAR_WIDTH,
            SCREEN_HEIGHT
        )
        pygame.draw.rect(self.screen, DARK_GRAY, sidebar_rect)
        pygame.draw.line(self.screen, LIGHT_GRAY, (sidebar_rect.left, 0), (sidebar_rect.left, SCREEN_HEIGHT), 2)

        # 显示下一个方块
        next_text = self.font.render("下一个:", True, WHITE)
        self.screen.blit(next_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 50))

        # 绘制下一个方块预览
        preview_x = SCREEN_WIDTH - SIDEBAR_WIDTH + 50
        preview_y = 100
        for r, row in enumerate(self.next_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        pygame.Rect(
                            preview_x + c * GRID_SIZE,
                            preview_y + r * GRID_SIZE,
                            GRID_SIZE - 2,
                            GRID_SIZE - 2
                        )
                    )

        # 显示分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 200))

        # 显示对手分数（对战模式）
        if self.game_mode != "single":
            opponent_text = self.font.render(f"{self.opponent_name}: {self.opponent_score}", True, WHITE)
            self.screen.blit(opponent_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 230))

        # 显示等级
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 270))

        # 显示消除行数
        lines_text = self.font.render(f"行数: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 300))

        # 显示对手行数
        if self.game_mode != "single":
            opponent_lines = self.font.render(f"对手行数: {self.opponent_lines}", True, WHITE)
            self.screen.blit(opponent_lines, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 330))

        # 显示游戏模式
        mode_text = self.small_font.render(f"模式: {self.game_mode}", True, YELLOW)
        self.screen.blit(mode_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 370))

        # 显示控制说明
        controls_y = 420
        controls = [
            "控制说明:",
            "← → : 移动",
            "↑ : 旋转",
            "↓ : 下降",
            "空格: 瞬降",
            "R : 重新开始",
            "ESC : 退出",
            "H : 创建对战",
            "C : 加入对战"
        ]

        for i, text in enumerate(controls):
            ctrl_text = self.small_font.render(text, True, LIGHT_GRAY)
            self.screen.blit(ctrl_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, controls_y + i * 25))

        # 显示游戏结束信息
        if self.game_over:
            game_over_text = self.font.render("游戏结束!", True, RED)
            restart_text = self.small_font.render("按 R 重新开始", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2))

    def send_battle_data(self):
        """发送对战数据给对手"""
        if self.bluetooth_manager and self.game_mode in ["host", "client"]:
            data = {
                "action": "game_update",
                "score": self.score,
                "lines": self.lines_cleared,
                "level": self.level,
                "game_over": self.game_over
            }
            self.bluetooth_manager.send_data(data)

    def receive_battle_data(self, data):
        """接收对手的对战数据"""
        if data.get("action") == "game_update":
            self.opponent_score = data.get("score", 0)
            self.opponent_lines = data.get("lines", 0)
            # 可以根据对手的行数来增加障碍行
            if data.get("game_over"):
                print("对手游戏结束")

        elif data.get("action") == "attack":
            attack_lines = data.get("lines", 0)
            self.add_obstacle_lines(attack_lines)

    def add_obstacle_lines(self, count):
        """添加对手攻击的障碍行"""
        for _ in range(count):
            # 删除顶部行
            self.grid.pop(0)
            # 在底部添加带障碍物的行
            new_line = [GRAY if random.random() > 0.2 else 0 for _ in range(GRID_WIDTH)]
            # 确保至少有一个空位
            empty_pos = random.randint(0, GRID_WIDTH - 1)
            new_line[empty_pos] = 0
            self.grid.append(new_line)

    def clear_lines(self):
        lines_cleared = 0
        lines_to_clear = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r]):
                lines_to_clear.append(r)

        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

        # 更新分数
        if lines_to_clear:
            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared
            self.score += [100, 300, 500, 800][min(lines_cleared - 1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

            # 发送攻击给对手（如果在对战模式下）
            if self.game_mode in ["host", "client"] and lines_cleared >= 2:
                attack_data = {
                    "action": "attack",
                    "lines": lines_cleared - 1  # 发送攻击行数
                }
                if self.bluetooth_manager:
                    self.bluetooth_manager.send_data(attack_data)

        return lines_cleared

    def run(self):
        last_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # 转换为秒
            last_time = current_time

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.bluetooth_manager:
                        self.bluetooth_manager.stop()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.bluetooth_manager:
                            self.bluetooth_manager.stop()
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_r:
                        self.reset_game()

                    # 对战模式控制
                    if event.key == pygame.K_h:  # 创建对战（作为主机）
                        self.start_battle_host()

                    if event.key == pygame.K_c:  # 加入对战（作为客户端）
                        self.start_battle_client()

                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.drop()

            # 自动下落
            if not self.game_over:
                self.fall_time += delta_time
                if self.fall_time >= self.fall_speed:
                    if not self.move(0, 1):
                        self.lock_piece()
                        # 发送游戏状态更新
                        self.send_battle_data()
                    self.fall_time = 0

            # 绘制游戏
            self.draw()
            self.clock.tick(60)

    def start_battle_host(self):
        """启动对战模式（作为主机）"""
        if BLUETOOTH_AVAILABLE:
            self.bluetooth_manager = BluetoothManager(is_host=True)
            self.bluetooth_manager.game = self
            self.bluetooth_manager.start()
            self.game_mode = "host"
            self.is_host = True
            print("已启动蓝牙对战主机模式")
        else:
            print("蓝牙不可用，使用模拟模式")
            self.bluetooth_manager = MockBluetoothManager(is_host=True)
            self.bluetooth_manager.game = self
            self.bluetooth_manager.start()
            self.game_mode = "host"
            self.is_host = True

    def start_battle_client(self):
        """启动对战模式（作为客户端）"""
        if BLUETOOTH_AVAILABLE:
            self.bluetooth_manager = BluetoothManager(is_host=False)
            self.bluetooth_manager.game = self
            self.bluetooth_manager.start()
            self.game_mode = "client"
            self.is_host = False
            print("已启动蓝牙对战客户端模式")
        else:
            print("蓝牙不可用，使用模拟模式")
            self.bluetooth_manager = MockBluetoothManager(is_host=False)
            self.bluetooth_manager.game = self
            self.bluetooth_manager.start()
            self.game_mode = "client"
            self.is_host = False


class BluetoothManager:
    def __init__(self, is_host=True):
        self.is_host = is_host
        self.game = None
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        if self.is_host:
            self._run_host()
        else:
            self._run_client()

    def _run_host(self):
        """运行主机模式"""
        try:
            # 这里应该实现蓝牙服务器逻辑
            # 由于Python蓝牙库在不同平台兼容性问题，这里使用模拟
            print("蓝牙主机模式启动（模拟）")
            while self.running:
                time.sleep(1)
                # 模拟接收数据
                if random.random() < 0.1:  # 10%概率收到数据
                    mock_data = {
                        "action": "game_update",
                        "score": random.randint(0, 1000),
                        "lines": random.randint(0, 20),
                        "level": random.randint(1, 5)
                    }
                    if self.game:
                        self.game.receive_battle_data(mock_data)
        except Exception as e:
            print(f"蓝牙主机错误: {e}")

    def _run_client(self):
        """运行客户端模式"""
        try:
            # 这里应该实现蓝牙客户端逻辑
            print("蓝牙客户端模式启动（模拟）")
            while self.running:
                time.sleep(1)
                # 模拟接收数据
                if random.random() < 0.1:  # 10%概率收到数据
                    mock_data = {
                        "action": "game_update",
                        "score": random.randint(0, 1000),
                        "lines": random.randint(0, 20),
                        "level": random.randint(1, 5)
                    }
                    if self.game:
                        self.game.receive_battle_data(mock_data)
        except Exception as e:
            print(f"蓝牙客户端错误: {e}")

    def send_data(self, data):
        """发送数据（模拟）"""
        # 在实际实现中，这里会通过蓝牙发送数据
        print(f"发送数据: {data}")


class MockBluetoothManager(BluetoothManager):
    """模拟蓝牙管理器，用于测试"""

    def __init__(self, is_host=True):
        super().__init__(is_host)

    def _run_host(self):
        print("模拟蓝牙主机启动")
        while self.running:
            time.sleep(2)
            # 模拟对手数据
            mock_data = {
                "action": "game_update",
                "score": random.randint(0, 2000),
                "lines": random.randint(0, 30),
                "level": random.randint(1, 10),
                "game_over": False
            }
            if self.game:
                # 使用pygame的事件队列来线程安全地更新游戏状态
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"data": mock_data}))

    def _run_client(self):
        print("模拟蓝牙客户端启动")
        while self.running:
            time.sleep(2)
            # 模拟对手数据
            mock_data = {
                "action": "game_update",
                "score": random.randint(0, 2000),
                "lines": random.randint(0, 30),
                "level": random.randint(1, 10),
                "game_over": False
            }
            if self.game:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"data": mock_data}))

    def send_data(self, data):
        print(f"模拟发送数据: {data}")


# 修改主运行部分
if __name__ == "__main__":
    # 检查命令行参数来设置游戏模式
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["single", "host", "client"], default="single")
    args = parser.parse_args()

    game = TetrisGame()

    # 根据命令行参数设置模式
    if args.mode == "host":
        game.start_battle_host()
    elif args.mode == "client":
        game.start_battle_client()

    game.run()

