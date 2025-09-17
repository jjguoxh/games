import pygame
import sys
import copy

# 初始化pygame
pygame.init()

# 常量定义
BOARD_SIZE = 19  # 19x19标准围棋棋盘
CELL_SIZE = 42   # 每个格子的大小 (30 * 1.4 = 42)
MARGIN = 70      # 边距 (50 * 1.4 = 70)
STONE_RADIUS = 17  # 棋子半径 (12 * 1.4 ≈ 17)

# 计算窗口大小
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + 2 * MARGIN
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + 2 * MARGIN + 100  # 额外空间用于显示信息

# 颜色定义
BACKGROUND_COLOR = (222, 184, 135)  # 棋盘背景色
LINE_COLOR = (0, 0, 0)              # 线条颜色
BLACK_STONE = (0, 0, 0)             # 黑子
WHITE_STONE = (255, 255, 255)       # 白子
HIGHLIGHT_COLOR = (255, 0, 0)       # 高亮颜色
TEXT_COLOR = (0, 0, 0)              # 文字颜色

class GoGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("围棋游戏")
        
        # 游戏状态
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # 0=空, 1=黑子, 2=白子
        self.current_player = 1  # 1=黑子先行, 2=白子
        self.game_over = False
        self.captured_black = 0  # 被吃掉的黑子数
        self.captured_white = 0  # 被吃掉的白子数
        
        # 历史记录用于打劫规则
        self.board_history = []
        self.last_capture_pos = None
        
        # 字体
        try:
            self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)
            self.small_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 18)
            print("成功加载中文字体")
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            print("使用默认字体")
    
    def draw_board(self):
        """绘制棋盘"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # 绘制网格线
        for i in range(BOARD_SIZE):
            # 垂直线
            start_x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (start_x, MARGIN), 
                           (start_x, MARGIN + (BOARD_SIZE - 1) * CELL_SIZE), 2)
            
            # 水平线
            start_y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (MARGIN, start_y), 
                           (MARGIN + (BOARD_SIZE - 1) * CELL_SIZE, start_y), 2)
        
        # 绘制星位点
        star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        for x, y in star_points:
            pos_x = MARGIN + x * CELL_SIZE
            pos_y = MARGIN + y * CELL_SIZE
            pygame.draw.circle(self.screen, LINE_COLOR, (pos_x, pos_y), 4)
    
    def draw_stones(self):
        """绘制棋子"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] != 0:
                    pos_x = MARGIN + col * CELL_SIZE
                    pos_y = MARGIN + row * CELL_SIZE
                    
                    color = BLACK_STONE if self.board[row][col] == 1 else WHITE_STONE
                    pygame.draw.circle(self.screen, color, (pos_x, pos_y), STONE_RADIUS)
                    
                    # 白子加黑边
                    if self.board[row][col] == 2:
                        pygame.draw.circle(self.screen, LINE_COLOR, (pos_x, pos_y), STONE_RADIUS, 2)
    
    def draw_info(self):
        """绘制游戏信息"""
        info_y = MARGIN + BOARD_SIZE * CELL_SIZE + 20
        
        # 当前玩家
        current_text = "当前玩家: " + ("黑子" if self.current_player == 1 else "白子")
        text_surface = self.font.render(current_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (MARGIN, info_y))
        
        # 被吃子数
        capture_text = f"被吃子数 - 黑子: {self.captured_black}, 白子: {self.captured_white}"
        text_surface = self.small_font.render(capture_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (MARGIN, info_y + 30))
        
        # 操作提示
        help_text = "左键落子 | R键重新开始 | ESC键退出"
        text_surface = self.small_font.render(help_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (MARGIN, info_y + 55))
    
    def get_board_position(self, mouse_pos):
        """将鼠标位置转换为棋盘坐标"""
        x, y = mouse_pos
        
        # 检查是否在棋盘范围内
        if x < MARGIN or x > MARGIN + (BOARD_SIZE - 1) * CELL_SIZE:
            return None
        if y < MARGIN or y > MARGIN + (BOARD_SIZE - 1) * CELL_SIZE:
            return None
        
        # 计算最近的交叉点
        col = round((x - MARGIN) / CELL_SIZE)
        row = round((y - MARGIN) / CELL_SIZE)
        
        # 确保在棋盘范围内
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        
        return None
    
    def get_neighbors(self, row, col):
        """获取相邻位置"""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_group(self, row, col):
        """获取连通的棋子组"""
        if self.board[row][col] == 0:
            return set()
        
        color = self.board[row][col]
        group = set()
        stack = [(row, col)]
        
        while stack:
            r, c = stack.pop()
            if (r, c) in group:
                continue
            
            group.add((r, c))
            
            for nr, nc in self.get_neighbors(r, c):
                if self.board[nr][nc] == color and (nr, nc) not in group:
                    stack.append((nr, nc))
        
        return group
    
    def count_liberties(self, group):
        """计算棋子组的气数"""
        liberties = set()
        
        for row, col in group:
            for nr, nc in self.get_neighbors(row, col):
                if self.board[nr][nc] == 0:
                    liberties.add((nr, nc))
        
        return len(liberties)
    
    def capture_stones(self, opponent_color):
        """吃掉没有气的对方棋子"""
        captured_positions = []
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == opponent_color:
                    group = self.get_group(row, col)
                    if group and self.count_liberties(group) == 0:
                        # 吃掉这组棋子
                        for r, c in group:
                            self.board[r][c] = 0
                            captured_positions.append((r, c))
                        
                        # 更新被吃子数
                        if opponent_color == 1:
                            self.captured_black += len(group)
                        else:
                            self.captured_white += len(group)
        
        return captured_positions
    
    def is_suicide_move(self, row, col, color):
        """检查是否为自杀手（禁入点）"""
        # 临时放置棋子
        self.board[row][col] = color
        
        # 检查自己的气
        my_group = self.get_group(row, col)
        my_liberties = self.count_liberties(my_group)
        
        # 检查是否能吃掉对方棋子
        opponent_color = 2 if color == 1 else 1
        can_capture = False
        
        for nr, nc in self.get_neighbors(row, col):
            if self.board[nr][nc] == opponent_color:
                opponent_group = self.get_group(nr, nc)
                if self.count_liberties(opponent_group) == 0:
                    can_capture = True
                    break
        
        # 恢复棋盘
        self.board[row][col] = 0
        
        # 如果没有气且不能吃子，则为自杀手
        return my_liberties == 0 and not can_capture
    
    def is_ko_violation(self, board_state):
        """检查是否违反打劫规则"""
        return board_state in self.board_history[-2:]  # 检查最近两步
    
    def make_move(self, row, col):
        """落子"""
        if self.game_over or self.board[row][col] != 0:
            return False
        
        # 检查是否为自杀手
        if self.is_suicide_move(row, col, self.current_player):
            print("禁入点，不能落子！")
            return False
        
        # 保存当前棋盘状态
        board_copy = copy.deepcopy(self.board)
        
        # 落子
        self.board[row][col] = self.current_player
        
        # 吃掉对方没有气的棋子
        opponent_color = 2 if self.current_player == 1 else 1
        captured = self.capture_stones(opponent_color)
        
        # 检查打劫规则
        current_board_state = copy.deepcopy(self.board)
        if self.is_ko_violation(current_board_state):
            print("违反打劫规则，不能落子！")
            self.board = board_copy  # 恢复棋盘
            return False
        
        # 记录棋盘状态
        self.board_history.append(current_board_state)
        if len(self.board_history) > 10:  # 只保留最近10步
            self.board_history.pop(0)
        
        # 切换玩家
        self.current_player = 2 if self.current_player == 1 else 1
        
        return True
    
    def reset_game(self):
        """重新开始游戏"""
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 1
        self.game_over = False
        self.captured_black = 0
        self.captured_white = 0
        self.board_history = []
        self.last_capture_pos = None
        print("游戏重新开始")
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    pos = self.get_board_position(event.pos)
                    if pos:
                        row, col = pos
                        self.make_move(row, col)
        
        return True
    
    def run(self):
        """主游戏循环"""
        clock = pygame.time.Clock()
        running = True
        
        print("围棋游戏开始！")
        print("操作说明：")
        print("- 左键点击交叉点落子")
        print("- R键重新开始游戏")
        print("- ESC键退出游戏")
        
        while running:
            running = self.handle_events()
            
            # 绘制游戏
            self.draw_board()
            self.draw_stones()
            self.draw_info()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GoGame()
    game.run()