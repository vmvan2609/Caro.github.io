from config import BOARD_SIZE, PLAYER_X, PLAYER_O

class Game:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.move_count = 0
        
    def make_move(self, row, col, player):
        if self.game_over:
            return False
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        if self.board[row][col] != 0:
            return False
        if player != self.current_player:
            return False
        
        self.board[row][col] = player
        self.last_move = (row, col)
        self.move_count += 1
        
        if self.check_win(row, col, player):
            self.game_over = True
            self.winner = player
            return True
        
        if self.is_draw():
            self.game_over = True
            return True
        
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
        return True
    
    def check_win(self, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            for step in range(1, 5):
                nx, ny = row + dx*step, col + dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if self.board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            for step in range(1, 5):
                nx, ny = row - dx*step, col - dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if self.board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                return True
        return False
    
    def is_draw(self):
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def reset(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.move_count = 0