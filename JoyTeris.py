# Tetris with battle function, add garbage lines to opponent after clearing lines

import pygame
import random
from pygame.locals import *
import socket
import threading
import json

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Color definitions
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

# Block shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

# Block colors
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
        # Transpose matrix and reverse rows to rotate clockwise
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

        # Update score
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [100, 300, 500, 800][min(len(lines_to_clear) - 1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1

        return len(lines_to_clear)

    def add_garbage_lines(self, num_lines):
        """Add garbage lines"""
        # Remove top lines
        for _ in range(num_lines):
            self.grid.pop(0)

        # Add new garbage lines at bottom
        for _ in range(num_lines):
            # Create random line with holes (ensure it's not a complete line to avoid immediate clear)
            garbage_line = [GRAY if random.random() > 0.3 else 0 for _ in range(GRID_WIDTH)]
            # Ensure at least one empty space to prevent immediate game over
            if all(garbage_line):
                garbage_line[random.randint(0, GRID_WIDTH - 1)] = 0
            self.grid.append(garbage_line)

        # Check if current piece overlaps with new lines
        if not self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y):
            # If overlapping, try to move piece up
            while not self.valid_position(self.current_piece, self.current_piece.x,
                                          self.current_piece.y) and self.current_piece.y >= 0:
                self.current_piece.y -= 1

            # If piece position cannot be adjusted, game over
            if self.current_piece.y < 0:
                self.game_over = True

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
        lines_cleared = self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        # Check game over
        if not self.valid_position(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.game_over = True

        return lines_cleared
    def update(self):
        if not self.game_over:
            if not self.move(0, 1):
                self.lock_piece()

class TetrisNetwork:
    def __init__(self):
        self.socket = None
        self.is_host = False
        self.connected = False
        self.listener_thread = None
        self.on_data_received = None
        self.on_connection_lost = None
        
    def host_game(self, port=12345):
        """Host a game room"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', port))
            self.socket.listen(1)
            self.is_host = True
            self.connected = True
            
            self.listener_thread = threading.Thread(target=self._listen_for_client)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
            return True, f"Waiting for opponent to connect on port {port}..."
        except Exception as e:
            return False, f"Failed to create room: {str(e)}"
    
    def join_game(self, host_ip, port=12345):
        """Join a game room"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host_ip, port))
            self.is_host = False
            self.connected = True
            
            self.listener_thread = threading.Thread(target=self._listen_for_data)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
            # Send connection confirmation message
            self.send_data({"type": "connected"})
            return True, "Successfully connected to opponent"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def _listen_for_client(self):
        """Listen for client connection (host side)"""
        try:
            conn, addr = self.socket.accept()
            self.socket = conn
            self.connected = True
            
            # Start listening for data
            self._listen_for_data()
        except Exception as e:
            self._handle_connection_error(e)
    
    def _listen_for_data(self):
        """Listen for data reception"""
        buffer = ""
        try:
            while self.connected:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        try:
                            message = json.loads(line)
                            if self.on_data_received:
                                self.on_data_received(message)
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            self._handle_connection_error(e)
    
    def _handle_connection_error(self, error):
        """Handle connection error"""
        self.connected = False
        if self.on_connection_lost:
            self.on_connection_lost(str(error))
    
    def send_data(self, data):
        """Send data"""
        if self.connected and self.socket:
            try:
                message = json.dumps(data) + '\n'
                self.socket.send(message.encode('utf-8'))
                return True
            except Exception:
                self.connected = False
                return False
        return False
    
    def disconnect(self):
        """Disconnect"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Create two game areas
        self.board1 = TetrisBoard(100, 50)
        self.board2 = TetrisBoard(700, 50)

        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        
        # Network battle related
        self.network_mode = False
        self.is_host = False
        self.network = None
        self.waiting_for_opponent = False
        self.opponent_connected = False
        self.opponent_game_over = False
        
        # Network interface related
        self.show_network_menu = True
        self.ip_input = ""
        self.port_input = "12345"
        self.network_message = ""
        self.input_active = "ip"  # IP input is active by default in network menu

    def init_network_game(self, is_host, ip_address=""):
        """Initialize network battle"""
        try:
            self.network = TetrisNetwork()
            self.network.on_data_received = self.handle_network_data
            self.network.on_connection_lost = self.handle_connection_lost
            self.is_host = is_host
            
            if is_host:
                success, message = self.network.host_game(int(self.port_input))
            else:
                success, message = self.network.join_game(ip_address, int(self.port_input))
                
            if success:
                self.network_message = message
                self.waiting_for_opponent = True
                return True
            else:
                self.network_message = message
                return False
        except Exception as e:
            self.network_message = f"Error: {str(e)}"
            return False
    
    def handle_network_data(self, data):
        """Handle received network data"""
        try:
            if data["type"] == "connected":
                self.opponent_connected = True
                self.waiting_for_opponent = False
                self.network_message = "Opponent connected, game start!"
                
            elif data["type"] == "move":
                if self.is_host:  # Host controls player 2
                    board = self.board2
                else:  # Client controls player 1
                    board = self.board1
                    
                if data["action"] == "left":
                    board.move(-1, 0)
                elif data["action"] == "right":
                    board.move(1, 0)
                elif data["action"] == "down":
                    board.move(0, 1)
                elif data["action"] == "rotate":
                    board.rotate_piece()
                elif data["action"] == "drop":
                    board.drop()
                    
            elif data["type"] == "lock_piece":
                if self.is_host:  # Host handles player 2 lock
                    board = self.board2
                else:  # Client handles player 1 lock
                    board = self.board1
                    
                lines_cleared = data["lines_cleared"]
                # Add garbage lines to opponent
                if lines_cleared > 0:
                    if self.is_host:
                        self.board1.add_garbage_lines(min(lines_cleared, 2))
                    else:
                        self.board2.add_garbage_lines(min(lines_cleared, 2))
                        
            elif data["type"] == "game_over":
                self.opponent_game_over = True
                self.network_message = "Opponent game over, you win!"
                
        except Exception as e:
            print(f"Error handling network data: {e}")
    
    def handle_connection_lost(self, error):
        """Handle connection loss"""
        self.network_message = f"Connection lost: {error}"
        self.opponent_connected = False
    
    def send_move(self, action):
        """Send move command"""
        if self.network and self.network.connected:
            data = {
                "type": "move",
                "action": action
            }
            self.network.send_data(data)
    
    def send_lock_piece(self, lines_cleared):
        """Send lock piece information"""
        if self.network and self.network.connected:
            data = {
                "type": "lock_piece",
                "lines_cleared": lines_cleared
            }
            self.network.send_data(data)
    
    def send_game_over(self):
        """Send game over information"""
        if self.network and self.network.connected:
            data = {
                "type": "game_over"
            }
            self.network.send_data(data)

    def draw_board(self, board, title):
        # Draw border
        pygame.draw.rect(self.screen, WHITE,
                         (board.x_offset - 5, board.y_offset - 5,
                          GRID_WIDTH * BLOCK_SIZE + 10, GRID_HEIGHT * BLOCK_SIZE + 10), 2)

        # Draw title
        title_text = self.font.render(title, True, WHITE)
        self.screen.blit(title_text, (board.x_offset + GRID_WIDTH * BLOCK_SIZE // 2 - title_text.get_width() // 2,
                                      board.y_offset - 40))

        # Draw grid
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY,
                                 (board.x_offset + c * BLOCK_SIZE,
                                  board.y_offset + r * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 1)

                # Draw placed blocks
                if board.grid[r][c]:
                    pygame.draw.rect(self.screen, board.grid[r][c],
                                     (board.x_offset + c * BLOCK_SIZE,
                                      board.y_offset + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                     (board.x_offset + c * BLOCK_SIZE,
                                      board.y_offset + r * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw current piece
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

        # Draw next piece preview
        next_text = self.small_font.render("Next:", True, WHITE)
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

        # Draw score and level
        score_text = self.small_font.render(f"Score: {board.score}", True, WHITE)
        level_text = self.small_font.render(f"Level: {board.level}", True, WHITE)
        lines_text = self.small_font.render(f"Lines: {board.lines_cleared}", True, WHITE)

        self.screen.blit(score_text, (board.x_offset, next_preview_y + 100))
        self.screen.blit(level_text, (board.x_offset, next_preview_y + 130))
        self.screen.blit(lines_text, (board.x_offset, next_preview_y + 160))

        # Draw game over prompt
        if board.game_over:
            game_over_text = self.font.render("Game Over", True, RED)
            self.screen.blit(game_over_text,
                             (board.x_offset + GRID_WIDTH * BLOCK_SIZE // 2 - game_over_text.get_width() // 2,
                              board.y_offset + GRID_HEIGHT * BLOCK_SIZE // 2))

    def draw_network_menu(self):
        """Draw network menu"""
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Tetris Network Battle", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Host game button
        pygame.draw.rect(self.screen, GREEN, (400, 200, 200, 50))
        host_text = self.font.render("Host Game", True, BLACK)
        self.screen.blit(host_text, (500 - host_text.get_width()//2, 215))
        
        # Join game button
        pygame.draw.rect(self.screen, BLUE, (400, 300, 200, 50))
        join_text = self.font.render("Join Game", True, WHITE)
        self.screen.blit(join_text, (500 - join_text.get_width()//2, 315))
        
        # IP input box
        ip_label = self.small_font.render("Opponent IP:", True, WHITE)
        self.screen.blit(ip_label, (300, 380))
        pygame.draw.rect(self.screen, WHITE, (450, 375, 200, 30))  # Always white for IP input
        ip_text = self.small_font.render(self.ip_input, True, BLACK)
        self.screen.blit(ip_text, (455, 380))
        
        # Port input box
        port_label = self.small_font.render("Port:", True, WHITE)
        self.screen.blit(port_label, (350, 420))
        pygame.draw.rect(self.screen, WHITE if self.input_active == "port" else GRAY, (450, 415, 100, 30))
        port_text = self.small_font.render(self.port_input, True, BLACK)
        self.screen.blit(port_text, (455, 420))
        
        # Status message
        if self.network_message:
            status_text = self.small_font.render(self.network_message, True, 
                                               GREEN if "Success" in self.network_message or "connected" in self.network_message else RED)
            self.screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, 460))
        
        # Start game button (only shown when opponent connected)
        if self.opponent_connected:
            pygame.draw.rect(self.screen, GREEN, (400, 500, 200, 50))
            start_text = self.font.render("Start Game", True, BLACK)
            self.screen.blit(start_text, (500 - start_text.get_width()//2, 515))
        
        # Back button
        pygame.draw.rect(self.screen, RED, (400, 600, 200, 50))
        back_text = self.font.render("Back", True, WHITE)
        self.screen.blit(back_text, (500 - back_text.get_width()//2, 615))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if self.show_network_menu:
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if self.input_active == "ip":
                            self.ip_input = self.ip_input[:-1]
                        elif self.input_active == "port":
                            self.port_input = self.port_input[:-1]
                    elif event.key == K_RETURN:
                        if self.input_active == "port":
                            self.input_active = "ip"
                        elif self.input_active == "ip":
                            self.input_active = "port"
                    elif event.key == K_TAB:
                        if self.input_active == "ip":
                            self.input_active = "port"
                        elif self.input_active == "port":
                            self.input_active = "ip"
                    else:
                        char = event.unicode
                        if self.input_active == "ip":
                            self.ip_input += char
                        elif self.input_active == "port":
                            if char.isdigit():
                                self.port_input += char
                
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Host button
                    if 400 <= mouse_pos[0] <= 600 and 200 <= mouse_pos[1] <= 250:
                        self.init_network_game(True)
                        self.input_active = "port"  # Switch to port input for host
                    # Join button
                    elif 400 <= mouse_pos[0] <= 600 and 300 <= mouse_pos[1] <= 350:
                        if self.ip_input:
                            self.init_network_game(False, self.ip_input)
                            self.input_active = "port"  # Switch to port input after joining
                        else:
                            # Keep focus on IP input if no IP entered
                            self.input_active = "ip"
                            self.network_message = "Please enter opponent's IP address"
                    # Start button
                    elif 400 <= mouse_pos[0] <= 600 and 500 <= mouse_pos[1] <= 550 and self.opponent_connected:
                        self.show_network_menu = False
                        self.network_mode = True
                    # Back button
                    elif 400 <= mouse_pos[0] <= 600 and 600 <= mouse_pos[1] <= 650:
                        self.__init__()  # Reset game
                        
            elif not self.network_mode:
                # Original local two-player controls
                if event.type == KEYDOWN:
                    # Player 1 controls (WASD + Space)
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

                    # Player 2 controls (Arrow keys)
                    elif event.key == K_LEFT:
                        self.board2.move(-1, 0)
                    elif event.key == K_RIGHT:
                        self.board2.move(1, 0)
                    elif event.key == K_DOWN:
                        self.board2.move(0, 1)
                    elif event.key == K_UP:
                        self.board2.rotate_piece()
                    elif event.key == K_RETURN:  # Enter key
                        self.board2.drop()

                    # Restart game
                    elif event.key == K_r:
                        self.__init__()
            else:
                # Network mode controls
                if event.type == KEYDOWN:
                    if self.is_host:
                        # Host controls player 1 (WASD + Space)
                        if event.key == K_a:
                            self.board1.move(-1, 0)
                            self.send_move("left")
                        elif event.key == K_d:
                            self.board1.move(1, 0)
                            self.send_move("right")
                        elif event.key == K_s:
                            self.board1.move(0, 1)
                            self.send_move("down")
                        elif event.key == K_w:
                            self.board1.rotate_piece()
                            self.send_move("rotate")
                        elif event.key == K_SPACE:
                            self.board1.drop()
                            self.send_move("drop")
                    else:
                        # Client controls player 2 (Arrow keys)
                        if event.key == K_LEFT:
                            self.board2.move(-1, 0)
                            self.send_move("left")
                        elif event.key == K_RIGHT:
                            self.board2.move(1, 0)
                            self.send_move("right")
                        elif event.key == K_DOWN:
                            self.board2.move(0, 1)
                            self.send_move("down")
                        elif event.key == K_UP:
                            self.board2.rotate_piece()
                            self.send_move("rotate")
                        elif event.key == K_RETURN:
                            self.board2.drop()
                            self.send_move("drop")

                    # Restart game
                    if event.key == K_r:
                        self.__init__()

        return True
    
    def update(self, delta_time):
        if self.network_mode:
            self.fall_time += delta_time

            # Adjust falling speed based on level
            current_fall_speed = max(50, self.fall_speed - (self.board1.level + self.board2.level) * 20)

            if self.fall_time >= current_fall_speed:
                # Update player 1 (host control)
                if self.is_host and not self.board1.game_over:
                    if not self.board1.move(0, 1):
                        lines_cleared = self.board1.lock_piece()
                        self.send_lock_piece(lines_cleared)
                        # If lines cleared, add garbage lines to opponent
                        if lines_cleared > 0:
                            self.board2.add_garbage_lines(min(lines_cleared, 2))

                # Update player 2 (client control)
                if not self.is_host and not self.board2.game_over:
                    if not self.board2.move(0, 1):
                        lines_cleared = self.board2.lock_piece()
                        self.send_lock_piece(lines_cleared)
                        # If lines cleared, add garbage lines to opponent
                        if lines_cleared > 0:
                            self.board1.add_garbage_lines(min(lines_cleared, 2))

                # Check game over
                if (self.is_host and self.board1.game_over) or (not self.is_host and self.board2.game_over):
                    self.send_game_over()

                self.fall_time = 0
        else:
            # Local mode update
            self.fall_time += delta_time

            # Adjust falling speed based on level
            current_fall_speed = max(50, self.fall_speed - (self.board1.level + self.board2.level) * 20)

            if self.fall_time >= current_fall_speed:
                # Update player 1
                if not self.board1.game_over:
                    if not self.board1.move(0, 1):
                        lines_cleared = self.board1.lock_piece()
                        # If lines cleared, add garbage lines to opponent
                        if lines_cleared > 0:
                            self.board2.add_garbage_lines(min(lines_cleared, 2))  # Add up to 2 lines

                # Update player 2
                if not self.board2.game_over:
                    if not self.board2.move(0, 1):
                        lines_cleared = self.board2.lock_piece()
                        # If lines cleared, add garbage lines to opponent
                        if lines_cleared > 0:
                            self.board1.add_garbage_lines(min(lines_cleared, 2))  # Add up to 2 lines

                self.fall_time = 0

    def draw(self):
        if self.show_network_menu:
            self.screen.fill(BLACK)
            self.draw_network_menu()
            pygame.display.flip()
        elif self.network_mode:
            self.screen.fill(BLACK)

            # Draw two game areas
            if self.is_host:
                self.draw_board(self.board1, "Me (WASD+Space)")
                self.draw_board(self.board2, "Opponent" + (" (Game Over)" if self.opponent_game_over else ""))
            else:
                self.draw_board(self.board1, "Opponent" + (" (Game Over)" if self.opponent_game_over else ""))
                self.draw_board(self.board2, "Me (Arrow Keys+Enter)")

            # Draw network status
            status = "Connected" if self.network and self.network.connected else "Disconnected"
            status_text = self.small_font.render(f"Network Status: {status}", True, WHITE)
            self.screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, SCREEN_HEIGHT - 60))
            
            # Draw control instructions
            controls_text = self.small_font.render("Press R to restart", True, WHITE)
            self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 30))

            pygame.display.flip()
        else:
            self.screen.fill(BLACK)

            # Draw two game areas
            self.draw_board(self.board1, "Player 1 (WASD+Space)")
            self.draw_board(self.board2, "Player 2 (Arrow Keys+Enter)")

            # Draw control instructions
            controls_text = self.small_font.render("Press R to restart", True, WHITE)
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