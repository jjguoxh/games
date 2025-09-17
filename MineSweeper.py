import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
GRID_SIZE = 25
GRID_WIDTH = 18
GRID_HEIGHT = 18
MINES_COUNT = 50

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
MAROON = (128, 0, 0)
CYAN = (0, 128, 128)
ORANGE = (255, 165, 0)

# 数字颜色
NUMBER_COLORS = [
    BLUE,  # 1
    GREEN,  # 2
    RED,  # 3
    PURPLE,  # 4
    MAROON,  # 5
    CYAN,  # 6
    BLACK,  # 7
    GRAY  # 8
]


class MineSweeper:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("扫雷游戏")
        self.clock = pygame.time.Clock()
        # 使用支持中文的字体
        # 尝试多个可能的字体路径
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
        ]
        
        font_loaded = False
        for path in font_paths:
            try:
                self.font = pygame.font.Font(path, 24)
                self.large_font = pygame.font.Font(path, 48)
                print(f"成功加载字体: {path}")
                font_loaded = True
                break
            except Exception as e:
                print(f"尝试加载字体 {path} 失败: {e}")
        
        if not font_loaded:
            print("所有中文字体加载失败，使用系统默认字体")
            self.font = pygame.font.SysFont(None, 24)
            self.large_font = pygame.font.SysFont(None, 48)
        self.reset_game()

    def reset_game(self):
        # 创建游戏网格
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.revealed = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.flagged = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.mines_count = MINES_COUNT
        # 用于跟踪鼠标按键状态
        self.left_mouse_pressed = False
        self.right_mouse_pressed = False
        self.chording = False  # 是否正在执行震雷操作
        self.chord_x = -1
        self.chord_y = -1

        # 初始化地雷位置（在第一次点击后放置，避免第一次点击就失败）

    def place_mines(self, first_x, first_y):
        # 随机放置地雷，避开第一次点击的位置
        mines_placed = 0
        while mines_placed < MINES_COUNT:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)

            # 确保不在第一次点击位置及其周围放置地雷
            if (abs(x - first_x) <= 1 and abs(y - first_y) <= 1) or self.grid[y][x] == -1:
                continue

            self.grid[y][x] = -1  # -1 表示地雷
            mines_placed += 1

        # 计算每个非地雷格子周围的地雷数
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != -1:
                    count = self.count_mines_around(x, y)
                    self.grid[y][x] = count

    def count_mines_around(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if self.grid[ny][nx] == -1:
                        count += 1
        return count

    def reveal(self, x, y):
        # 如果是第一次点击，放置地雷
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        # 检查边界
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return

        # 如果已经翻开或标记了旗帜，不处理
        if self.revealed[y][x] or self.flagged[y][x]:
            return

        # 翻开格子
        self.revealed[y][x] = True

        # 如果点击到地雷，游戏结束
        if self.grid[y][x] == -1:
            self.game_over = True
            return

        # 如果是空白格子（周围没有地雷），自动翻开周围的格子
        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    self.reveal(x + dx, y + dy)

    def chord(self, x, y):
        """
        震雷功能：当一个数字格子周围已经标记了正确数量的旗帜时，
        可以翻开周围所有未标记的格子
        """
        # 检查边界
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return

        # 只有已翻开的数字格子才能触发震雷
        if not self.revealed[y][x] or self.grid[y][x] <= 0:
            return

        # 计算周围标记的旗帜数量
        flagged_count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if self.flagged[ny][nx]:
                        flagged_count += 1

        # 如果旗帜数量等于该格子显示的数字，则翻开周围所有未标记的格子
        if flagged_count == self.grid[y][x]:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    # 检查边界
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        # 翻开未标记且未翻开的格子
                        if not self.flagged[ny][nx] and not self.revealed[ny][nx]:
                            self.reveal(nx, ny)

    def toggle_flag(self, x, y):
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return
        if not self.revealed[y][x]:
            self.flagged[y][x] = not self.flagged[y][x]

    def check_win(self):
        # 检查是否所有非地雷格子都已翻开
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return False
        return True

    def draw(self):
        self.screen.fill(WHITE)

        # 计算网格起始位置使其居中
        grid_width_px = GRID_WIDTH * GRID_SIZE
        grid_height_px = GRID_HEIGHT * GRID_SIZE
        start_x = (SCREEN_WIDTH - grid_width_px) // 2
        start_y = (SCREEN_HEIGHT - grid_height_px) // 2 + 20

        # 绘制网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    start_x + x * GRID_SIZE,
                    start_y + y * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )

                # 绘制格子
                if self.revealed[y][x]:
                    # 已翻开的格子
                    if self.grid[y][x] == -1:
                        # 地雷
                        pygame.draw.rect(self.screen, RED, rect)
                        # 绘制地雷符号
                        pygame.draw.circle(self.screen, BLACK,
                                           (rect.centerx, rect.centery),
                                           GRID_SIZE // 3)
                    else:
                        # 数字格子
                        pygame.draw.rect(self.screen, GRAY, rect)
                        # 绘制数字
                        if self.grid[y][x] > 0:
                            text = self.font.render(str(self.grid[y][x]), True, NUMBER_COLORS[self.grid[y][x] - 1])
                            text_rect = text.get_rect(center=rect.center)
                            self.screen.blit(text, text_rect)
                else:
                    # 未翻开的格子
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    # 绘制旗帜
                    if self.flagged[y][x]:
                        pygame.draw.polygon(self.screen, RED, [
                            (rect.centerx, rect.top + 5),
                            (rect.centerx - 5, rect.top + 10),
                            (rect.centerx + 5, rect.top + 10)
                        ])
                        pygame.draw.line(self.screen, BLACK,
                                         (rect.centerx, rect.top + 10),
                                         (rect.centerx, rect.bottom - 5), 2)

                # 如果正在执行震雷操作，高亮显示目标格子
                if self.chording and x == self.chord_x and y == self.chord_y:
                    pygame.draw.rect(self.screen, (200, 200, 0), rect, 3)  # 黄色边框表示目标格子

        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, BLACK,
                             (start_x + x * GRID_SIZE, start_y),
                             (start_x + x * GRID_SIZE, start_y + grid_height_px))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, BLACK,
                             (start_x, start_y + y * GRID_SIZE),
                             (start_x + grid_width_px, start_y + y * GRID_SIZE))

        # 显示地雷数量
        mines_text = self.font.render(f"地雷数量: {self.mines_count}", True, BLACK)
        self.screen.blit(mines_text, (20, 20))

        # 显示操作提示
        hint_text = self.font.render("提示: 同时按下左右键可触发震雷", True, (0, 100, 0))
        self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, 20))

        # 显示游戏状态
        if self.game_over:
            game_over_text = self.large_font.render("游戏结束! 按R重新开始", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(game_over_text, text_rect)
        elif self.check_win():
            win_text = self.large_font.render("恭喜获胜! 按R重新开始", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(win_text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if not self.game_over:
                    # 处理鼠标按键按下事件
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # 获取鼠标位置
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        # 计算网格起始位置
                        grid_width_px = GRID_WIDTH * GRID_SIZE
                        grid_height_px = GRID_HEIGHT * GRID_SIZE
                        start_x = (SCREEN_WIDTH - grid_width_px) // 2
                        start_y = (SCREEN_HEIGHT - grid_height_px) // 2 + 20

                        # 检查点击是否在网格内
                        if (start_x <= mouse_x < start_x + grid_width_px and
                                start_y <= mouse_y < start_y + grid_height_px):
                            # 计算点击的格子坐标
                            grid_x = (mouse_x - start_x) // GRID_SIZE
                            grid_y = (mouse_y - start_y) // GRID_SIZE

                            # 记录按键状态
                            if event.button == 1:  # 左键
                                self.left_mouse_pressed = True
                            elif event.button == 3:  # 右键
                                self.right_mouse_pressed = True

                            # 如果左右键都按下，执行震雷操作
                            if self.left_mouse_pressed and self.right_mouse_pressed:
                                self.chording = True
                                self.chord_x = grid_x
                                self.chord_y = grid_y
                                self.chord(grid_x, grid_y)
                            # 如果只是单击左键，且没有在震雷状态，则翻开格子
                            elif event.button == 1 and not self.chording and not self.right_mouse_pressed:
                                self.reveal(grid_x, grid_y)
                            # 如果只是单击右键，且没有在震雷状态，则标记旗帜
                            elif event.button == 3 and not self.chording and not self.left_mouse_pressed:
                                self.toggle_flag(grid_x, grid_y)

                    # 处理鼠标按键释放事件
                    elif event.type == pygame.MOUSEBUTTONUP:
                        # 获取鼠标位置
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        # 计算网格起始位置
                        grid_width_px = GRID_WIDTH * GRID_SIZE
                        grid_height_px = GRID_HEIGHT * GRID_SIZE
                        start_x = (SCREEN_WIDTH - grid_width_px) // 2
                        start_y = (SCREEN_HEIGHT - grid_height_px) // 2 + 20

                        # 检查点击是否在网格内
                        if (start_x <= mouse_x < start_x + grid_width_px and
                                start_y <= mouse_y < start_y + grid_height_px):
                            # 计算点击的格子坐标
                            grid_x = (mouse_x - start_x) // GRID_SIZE
                            grid_y = (mouse_y - start_y) // GRID_SIZE

                            # 处理按键释放
                            if event.button == 1:  # 左键释放
                                self.left_mouse_pressed = False
                            elif event.button == 3:  # 右键释放
                                self.right_mouse_pressed = False

                            # 重置震雷状态
                            self.chording = False
                            self.chord_x = -1
                            self.chord_y = -1
                        else:
                            # 点击在网格外，重置按键状态
                            if event.button == 1:
                                self.left_mouse_pressed = False
                            elif event.button == 3:
                                self.right_mouse_pressed = False
                            self.chording = False
                            self.chord_x = -1
                            self.chord_y = -1

            self.draw()
            self.clock.tick(60)


# 运行游戏
if __name__ == "__main__":
    game = MineSweeper()
    game.run()
