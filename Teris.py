import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

# 方块颜色
COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]


class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.rotation = 0

    def rotate(self):
        # 转置矩阵实现旋转
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]

        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]

        return rotated


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

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

    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0)

    def valid_position(self, piece, x, y, shape=None):
        shape_to_check = shape if shape else piece.shape

        for r, row in enumerate(shape_to_check):
            for c, cell in enumerate(row):
                if cell:
                    pos_x, pos_y = x + c, y + r
                    # 检查边界
                    if pos_x < 0 or pos_x >= GRID_WIDTH or pos_y >= GRID_HEIGHT:
                        return False
                    # 检查是否与已有方块重叠
                    if pos_y >= 0 and self.grid[pos_y][pos_x]:
                        return False
        return True

    def merge_piece(self):
        for r, row in enumerate(self.current_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pos_y = self.current_piece.y + r
                    pos_x = self.current_piece.x + c
                    if pos_y >= 0:  # 只合并可见区域内的方块
                        self.grid[pos_y][pos_x] = self.current_piece.color

    def clear_lines(self):
        lines_to_clear = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r]):
                lines_to_clear.append(r)

        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

        # 更新分数
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [100, 300, 500, 800][min(len(lines_to_clear) - 1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

        return len(lines_to_clear)

    def move(self, dx, dy):
        if not self.game_over:
            if self.valid_position(self.current_piece, self.current_piece.x + dx, self.current_piece.y + dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return True
        return False

    def rotate_piece(self):
        if not self.game_over:
            rotated_shape = self.current_piece.rotate()
            if self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y, rotated_shape):
                self.current_piece.shape = rotated_shape
                return True
        return False

    def drop(self):
        if not self.game_over:
            while self.move(0, 1):
                pass
            self.lock_piece()

    def lock_piece(self):
        self.merge_piece()
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        # 检查游戏结束
        if not self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.game_over = True

    def draw_grid(self):
        # 绘制游戏区域背景
        game_area_rect = pygame.Rect(
            (SCREEN_WIDTH - SIDEBAR_WIDTH) // 2 - GRID_WIDTH * GRID_SIZE // 2,
            50,
            GRID_WIDTH * GRID_SIZE,
            GRID_HEIGHT * GRID_SIZE
        )
        pygame.draw.rect(self.screen, DARK_GRAY, game_area_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, game_area_rect, 2)

        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (game_area_rect.left + x * GRID_SIZE, game_area_rect.top),
                (game_area_rect.left + x * GRID_SIZE, game_area_rect.bottom)
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (game_area_rect.left, game_area_rect.top + y * GRID_SIZE),
                (game_area_rect.right, game_area_rect.top + y * GRID_SIZE)
            )

        # 绘制已落下的方块
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c]:
                    pygame.draw.rect(
                        self.screen,
                        self.grid[r][c],
                        pygame.Rect(
                            game_area_rect.left + c * GRID_SIZE + 1,
                            game_area_rect.top + r * GRID_SIZE + 1,
                            GRID_SIZE - 2,
                            GRID_SIZE - 2
                        )
                    )

        # 绘制当前方块
        if not self.game_over:
            for r, row in enumerate(self.current_piece.shape):
                for c, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen,
                            self.current_piece.color,
                            pygame.Rect(
                                game_area_rect.left + (self.current_piece.x + c) * GRID_SIZE + 1,
                                game_area_rect.top + (self.current_piece.y + r) * GRID_SIZE + 1,
                                GRID_SIZE - 2,
                                GRID_SIZE - 2
                            )
                        )

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

        # 显示等级
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 250))

        # 显示消除行数
        lines_text = self.font.render(f"行数: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 300))

        # 显示控制说明
        controls_y = 400
        controls = [
            "控制说明:",
            "← → : 移动",
            "↑ : 旋转",
            "↓ : 下降",
            "空格: 瞬降",
            "R : 重新开始",
            "ESC : 退出"
        ]

        for i, text in enumerate(controls):
            ctrl_text = self.small_font.render(text, True, LIGHT_GRAY)
            self.screen.blit(ctrl_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, controls_y + i * 30))

        # 显示游戏结束信息
        if self.game_over:
            game_over_text = self.font.render("游戏结束!", True, RED)
            restart_text = self.small_font.render("按 R 重新开始", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_sidebar()
        pygame.display.flip()

    def run(self):
        last_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # 转换为秒
            last_time = current_time

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_r:
                        self.reset_game()

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
                    self.fall_time = 0

            # 绘制游戏
            self.draw()
            self.clock.tick(60)


# 运行游戏
if __name__ == "__main__":
    game = TetrisGame()
    game.run()
