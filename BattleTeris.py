# 追站俄罗斯方块
import pygame
import random
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# 方块形状
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
        # 转置矩阵并翻转行实现顺时针旋转
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        return rotated


class TetrisBoard:
    def __init__(self, x_offset, y_offset):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0)

    def valid_position(self, piece, x, y, shape=None):
        shape_to_check = shape if shape else piece.shape
        for r, row in enumerate(shape_to_check):
            for c, cell in enumerate(row):
                if cell:
                    pos_x, pos_y = x + c, y + r
                    if (pos_x < 0 or pos_x >= GRID_WIDTH or
                            pos_y >= GRID_HEIGHT or
                            (pos_y >= 0 and self.grid[pos_y][pos_x])):
                        return False
        return True

    def merge_piece(self):
        for r, row in enumerate(self.current_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pos_y = self.current_piece.y + r
                    pos_x = self.current_piece.x + c
                    if 0 <= pos_y < GRID_HEIGHT and 0 <= pos_x < GRID_WIDTH:
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

    def update(self):
        if not self.game_over:
            if not self.move(0, 1):
                self.lock_piece()


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("双人俄罗斯方块对战")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # 创建两个游戏区域
        self.board1 = TetrisBoard(100, 50)
        self.board2 = TetrisBoard(700, 50)

        self.fall_time = 0
        self.fall_speed = 500  # 毫秒

    def draw_board(self, board, title):
        # 绘制边框
        pygame.draw.rect(self.screen, WHITE,
                         (board.x_offset - 5, board.y_offset - 5,
                          GRID_WIDTH * BLOCK_SIZE + 10, GRID_HEIGHT * BLOCK_SIZE + 10), 2)

        # 绘制标题
        title_text = self.font.render(title, True, WHITE)
        self.screen.blit(title_text, (board.x_offset + GRID_WIDTH * BLOCK_SIZE // 2 - title_text.get_width() // 2,
                                      board.y_offset - 40))

        # 绘制网格
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY,
                                 (board.x_offset + c * BLOCK_SIZE,
                                  board.y_offset + r * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 1)

                # 绘制已放置的方块
                if board.grid[r][c]:
                    pygame.draw.rect(self.screen, board.grid[r][c],
                                     (board.x_offset + c * BLOCK_SIZE,
                                      board.y_offset + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                     (board.x_offset + c * BLOCK_SIZE,
                                      board.y_offset + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

        # 绘制当前方块
        if not board.game_over:
            for r, row in enumerate(board.current_piece.shape):
                for c, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, board.current_piece.color,
                                         (board.x_offset + (board.current_piece.x + c) * BLOCK_SIZE,
                                          board.y_offset + (board.current_piece.y + r) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, WHITE,
                                         (board.x_offset + (board.current_piece.x + c) * BLOCK_SIZE,
                                          board.y_offset + (board.current_piece.y + r) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 1)

        # 绘制下一个方块预览
        next_text = self.small_font.render("下一个:", True, WHITE)
        self.screen.blit(next_text, (board.x_offset, board.y_offset + GRID_HEIGHT * BLOCK_SIZE + 20))

        next_preview_x = board.x_offset
        next_preview_y = board.y_offset + GRID_HEIGHT * BLOCK_SIZE + 50

        for r, row in enumerate(board.next_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, board.next_piece.color,
                                     (next_preview_x + c * BLOCK_SIZE,
                                      next_preview_y + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                     (next_preview_x + c * BLOCK_SIZE,
                                      next_preview_y + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

        # 绘制分数和等级
        score_text = self.small_font.render(f"分数: {board.score}", True, WHITE)
        level_text = self.small_font.render(f"等级: {board.level}", True, WHITE)
        lines_text = self.small_font.render(f"行数: {board.lines_cleared}", True, WHITE)

        self.screen.blit(score_text, (board.x_offset, next_preview_y + 100))
        self.screen.blit(level_text, (board.x_offset, next_preview_y + 130))
        self.screen.blit(lines_text, (board.x_offset, next_preview_y + 160))

        # 绘制游戏结束提示
        if board.game_over:
            game_over_text = self.font.render("游戏结束", True, RED)
            self.screen.blit(game_over_text,
                             (board.x_offset + GRID_WIDTH * BLOCK_SIZE // 2 - game_over_text.get_width() // 2,
                              board.y_offset + GRID_HEIGHT * BLOCK_SIZE // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if event.type == KEYDOWN:
                # 玩家1控制 (WASD + 空格)
                if event.key == K_a:
                    self.board1.move(-1, 0)
                elif event.key == K_d:
                    self.board1.move(1, 0)
                elif event.key == K_s:
                    self.board1.move(0, 1)
                elif event.key == K_w:
                    self.board1.rotate_piece()
                elif event.key == K_SPACE:
                    self.board1.drop()

                # 玩家2控制 (方向键)
                elif event.key == K_LEFT:
                    self.board2.move(-1, 0)
                elif event.key == K_RIGHT:
                    self.board2.move(1, 0)
                elif event.key == K_DOWN:
                    self.board2.move(0, 1)
                elif event.key == K_UP:
                    self.board2.rotate_piece()
                elif event.key == K_RETURN:  # 回车键
                    self.board2.drop()

                # 重新开始游戏
                elif event.key == K_r:
                    self.__init__()

        return True

    def update(self, delta_time):
        self.fall_time += delta_time

        # 根据等级调整下落速度
        current_fall_speed = max(50, self.fall_speed - (self.board1.level + self.board2.level) * 20)

        if self.fall_time >= current_fall_speed:
            self.board1.update()
            self.board2.update()
            self.fall_time = 0

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制两个游戏区域
        self.draw_board(self.board1, "玩家1 (WASD+空格)")
        self.draw_board(self.board2, "玩家2 (方向键+回车)")

        # 绘制控制说明
        controls_text = self.small_font.render("R键重新开始", True, WHITE)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60)

            running = self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
