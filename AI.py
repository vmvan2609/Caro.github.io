from config import BOARD_SIZE, NEIGHBOR_RADIUS, MAX_CANDIDATES
from config import DEFENSE_WEIGHT
from config import PLAYER_X, PLAYER_O

class AI:
    def __init__(self, player_symbol=PLAYER_O, opponent_symbol=PLAYER_X, depth=3):
        self.player = player_symbol
        self.opponent = opponent_symbol
        self.max_depth = depth
        self.nodes_visited = 0
        self.pruned_branches = 0
        
    def get_best_move(self, board):
        self.nodes_visited = 0
        self.pruned_branches = 0
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        candidates = self.get_candidate_moves(board)
        
        if not candidates:
            return None
        
        candidates = self.order_moves_by_heuristic(board, candidates)
        
        for move in candidates:
            row, col = move
            board[row][col] = self.player
            move_value = self.minimax_alpha_beta(board, 0, alpha, beta, False)
            board[row][col] = 0
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
            
            alpha = max(alpha, move_value)
        
        return best_move
    
    def minimax_alpha_beta(self, board, depth, alpha, beta, is_maximizing):
        self.nodes_visited += 1
        
        if self.check_win(board, self.player):
            return 1000000 - depth
        
        if self.check_win(board, self.opponent):
            return -1000000 + depth
        
        if depth >= self.max_depth:
            return self.evaluate_board(board)
        
        candidates = self.get_candidate_moves(board)
        if not candidates:
            return self.evaluate_board(board)
        
        candidates = self.order_moves_by_heuristic(board, candidates)
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in candidates:
                row, col = move
                board[row][col] = self.player
                eval_score = self.minimax_alpha_beta(board, depth + 1, alpha, beta, False)
                board[row][col] = 0
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in candidates:
                row, col = move
                board[row][col] = self.opponent
                eval_score = self.minimax_alpha_beta(board, depth + 1, alpha, beta, True)
                board[row][col] = 0
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return min_eval
    
    def get_candidate_moves(self, board):
        moves = set()
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] != 0:
                    for di in range(-NEIGHBOR_RADIUS, NEIGHBOR_RADIUS + 1):
                        for dj in range(-NEIGHBOR_RADIUS, NEIGHBOR_RADIUS + 1):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                                if board[ni][nj] == 0:
                                    moves.add((ni, nj))
        
        if not moves:
            center = BOARD_SIZE // 2
            moves.add((center, center))
            for di in range(-2, 3):
                for dj in range(-2, 3):
                    ni, nj = center + di, center + dj
                    if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                        if board[ni][nj] == 0:
                            moves.add((ni, nj))
        
        return list(moves)
    
    def order_moves_by_heuristic(self, board, moves):
        scored_moves = []
        for move in moves:
            score = self.heuristic_evaluate_move(board, move[0], move[1])
            scored_moves.append((move[0], move[1], score))
        scored_moves.sort(key=lambda x: x[2], reverse=True)
        return [(m[0], m[1]) for m in scored_moves[:MAX_CANDIDATES]]
    
    def heuristic_evaluate_move(self, board, row, col):
        score = 0
        score += self.evaluate_position_fast(board, row, col, self.player)
        score += self.evaluate_position_fast(board, row, col, self.opponent) * DEFENSE_WEIGHT
        return score
    
    def evaluate_position_fast(self, board, row, col, player):
        total = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            for step in range(1, 5):
                nx, ny = row + dx*step, col + dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            for step in range(1, 5):
                nx, ny = row - dx*step, col - dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                total += 100000
            elif count == 4:
                total += 10000
            elif count == 3:
                total += 1000
            elif count == 2:
                total += 100
            elif count == 1:
                total += 10
        
        return total
    
    def evaluate_board(self, board):
        total_score = 0
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == self.player:
                    total_score += self.evaluate_position(board, i, j, self.player)
                elif board[i][j] == self.opponent:
                    total_score -= self.evaluate_position(board, i, j, self.opponent) * DEFENSE_WEIGHT
        
        return total_score
    
    def evaluate_position(self, board, row, col, player):
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            left_open = False
            right_open = False
            
            for step in range(1, 5):
                nx, ny = row + dx*step, col + dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    if board[nx][ny] == 0:
                        right_open = True
                    break
            
            for step in range(1, 5):
                nx, ny = row - dx*step, col - dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    if board[nx][ny] == 0:
                        left_open = True
                    break
            
            score += self.get_chain_score(count, left_open and right_open, left_open or right_open)
        
        return score
    
    def get_chain_score(self, length, is_double_open, is_single_open):
        if length >= 5:
            return 1000000
        
        if length == 4:
            if is_double_open:
                return 200000
            elif is_single_open:
                return 50000
            return 5000
        
        if length == 3:
            if is_double_open:
                return 20000
            elif is_single_open:
                return 3000
            return 300
        
        if length == 2:
            if is_double_open:
                return 800
            elif is_single_open:
                return 100
            return 20
        
        if length == 1:
            return 5
        
        return 0
    
    def check_win(self, board, player):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == player:
                    if self.check_win_at(board, i, j, player):
                        return True
        return False
    
    def check_win_at(self, board, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            for step in range(1, 5):
                nx, ny = row + dx*step, col + dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            for step in range(1, 5):
                nx, ny = row - dx*step, col - dy*step
                if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
                    break
                if board[nx][ny] == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                return True
        return False