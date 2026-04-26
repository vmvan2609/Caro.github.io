import tkinter as tk
from tkinter import messagebox
import time
from config import BOARD_SIZE, CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from config import BG_COLOR, LINE_COLOR, PLAYER_X_COLOR, PLAYER_O_COLOR, HIGHLIGHT_COLOR
from config import PLAYER_X, PLAYER_O
from game import Game
from AI import AI

class CaroGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Caro AI")
        
        self.root.overrideredirect(False)
        self.root.wm_attributes('-toolwindow', False)
        self.root.state('normal')
        
        window_width = WINDOW_WIDTH + 50
        window_height = WINDOW_HEIGHT + 160
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Căn giữa màn hình
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        
        if y < 20:
            y = 20
        if y + window_height > screen_height - 40:
            y = screen_height - window_height - 40
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Cho phép resize để hiển thị nút
        self.root.resizable(True, True)
        
        self.root.configure(bg='#2C3E50')
        
        self.game = Game()
        self.ai = AI()
        self.ai_thinking = False
        self.auto_reset_timer = None
        self.difficulty = tk.StringVar(value="Medium")
        self.setup_ui()
        
    def setup_ui(self):
        # HEADER THU GỌN
        header_frame = tk.Frame(self.root, bg='#2C3E50', height=45)
        header_frame.pack(fill=tk.X, padx=15, pady=(5, 2))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="CARO", 
                              font=('Helvetica', 12, 'bold'), 
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=(10, 0))
        
        # TOOLBAR THU GỌN
        toolbar_frame = tk.Frame(self.root, bg='#34495E', height=38)
        toolbar_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        toolbar_frame.pack_propagate(False)
        
        # Nút NEW GAME
        newgame_btn = tk.Button(toolbar_frame, text="NEW GAME", command=self.new_game, 
                              font=('Helvetica', 9, 'bold'), bg='#27AE60', fg='white', 
                              padx=15, pady=4, cursor='hand2', relief=tk.FLAT,
                              activebackground='#2ECC71', activeforeground='white')
        newgame_btn.pack(side=tk.LEFT, padx=10, pady=4)
        
        # Nút EXIT
        exit_btn = tk.Button(toolbar_frame, text="EXIT", command=self.exit_game, 
                            font=('Helvetica', 9, 'bold'), bg='#E74C3C', fg='white', 
                            padx=15, pady=4, cursor='hand2', relief=tk.FLAT,
                            activebackground='#C0392B', activeforeground='white')
        exit_btn.pack(side=tk.LEFT, padx=10, pady=4)
        
        # Chọn độ khó
        tk.Label(
            toolbar_frame,
            text="Difficulty:",
            font=('Helvetica', 9, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        difficulty_menu = tk.OptionMenu(
            toolbar_frame,
            self.difficulty,
            "Easy",
            "Medium",
            "Hard"
        )

        difficulty_menu.config(
            font=('Helvetica', 8),
            bg='white',
            width=8
        )

        difficulty_menu.pack(
            side=tk.LEFT,
            padx=5,
            pady=4
        )
       
        status_frame = tk.Frame(toolbar_frame, bg='#2C3E50', relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.RIGHT, padx=15, pady=4, fill=tk.Y)
        
        self.status_label = tk.Label(status_frame, text="LUOT CUA BAN (X)", 
                                      font=('Helvetica', 9, 'bold'), 
                                      fg='#F39C12', bg='#2C3E50', padx=10, pady=2)
        self.status_label.pack()
        
        # BÀN CỜ
        board_container = tk.Frame(self.root, bg='#8B6914', relief=tk.RAISED, bd=3)
        board_container.pack(pady=8, padx=15)
        
        self.canvas = tk.Canvas(board_container, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, 
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        
        # FOOTER THU GỌN 
        footer_frame = tk.Frame(self.root, bg='#2C3E50')
        # Khung thông kê AI
        stats_frame = tk.Frame(
            self.root,
            bg='#34495E',
            relief=tk.RAISED,
            bd=2
        )
        stats_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.stats_label = tk.Label(
            stats_frame,
                text="AI Stats | Nodes: 0 | Pruned: 0 | Time: 0.00s",
                font=('Helvetica', 9, 'bold'),
                fg='white',
                bg='#34495E',
                pady=5
        )
        self.stats_label.pack()
        
        footer_frame.pack(fill=tk.X, padx=15, pady=(5, 8))
        
        self.timer_label = tk.Label(footer_frame, text="", font=('Helvetica', 7, 'italic'), 
                                    fg='#F39C12', bg='#2C3E50')
        self.timer_label.pack(pady=2)
        
        self.draw_board()
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)
        self.hover_id = None
        
        self.root.bind('<n>', lambda e: self.new_game())
        self.root.bind('<N>', lambda e: self.new_game())
        self.root.bind('<Escape>', lambda e: self.exit_game())
    
    def on_hover(self, event):
        if self.ai_thinking or self.game.game_over:
            return
        
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.game.board[row][col] == 0 and self.game.current_player == PLAYER_X:
                if self.hover_id:
                    self.canvas.delete(self.hover_id)
                
                x1 = col * CELL_SIZE + 3
                y1 = row * CELL_SIZE + 3
                x2 = (col + 1) * CELL_SIZE - 3
                y2 = (row + 1) * CELL_SIZE - 3
                
                self.hover_id = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                              outline='#F39C12', width=2, dash=(4, 4))
    
    def draw_board(self):
        self.canvas.delete("all")
        
        # Dùng CELL_SIZE và BOARD_SIZE từ config
        size = CELL_SIZE
        width = BOARD_SIZE * size
        height = BOARD_SIZE * size
        
        # Đảm bảo canvas có kích thước đúng
        self.canvas.config(width=width, height=height)
        
        self.canvas.create_rectangle(0, 0, width, height, fill=BG_COLOR, outline='')
        
        for i in range(BOARD_SIZE):
            self.canvas.create_line(0, i * size, width, i * size, 
                                   fill=LINE_COLOR, width=1)
            self.canvas.create_line(i * size, 0, i * size, height, 
                                   fill=LINE_COLOR, width=1)
        
        if self.game.last_move:
            row, col = self.game.last_move
            x1 = col * size + 3
            y1 = row * size + 3
            x2 = x1 + size - 6
            y2 = y1 + size - 6
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=HIGHLIGHT_COLOR, outline='', stipple='gray50')
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.game.board[i][j] == PLAYER_X:
                    self.draw_x(i, j)
                elif self.game.board[i][j] == PLAYER_O:
                    self.draw_o(i, j)
    
    def draw_x(self, row, col):
        margin = 7
        x1 = col * CELL_SIZE + margin
        y1 = row * CELL_SIZE + margin
        x2 = (col + 1) * CELL_SIZE - margin
        y2 = (row + 1) * CELL_SIZE - margin
        
        line_width = 3
        
        self.canvas.create_line(x1, y1, x2, y2, fill=PLAYER_X_COLOR, width=line_width, capstyle='round')
        self.canvas.create_line(x2, y1, x1, y2, fill=PLAYER_X_COLOR, width=line_width, capstyle='round')
    
    def draw_o(self, row, col):
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 7
        
        line_width = 3
        
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=PLAYER_O_COLOR, width=line_width)
    
    def on_click(self, event):
        if self.ai_thinking or self.game.game_over:
            return
        
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.game.current_player != PLAYER_X:
                return
            if self.game.board[row][col] != 0:
                return
            
            if self.game.make_move(row, col, PLAYER_X):
                self.draw_board()
                self.root.update()
                
                if self.game.game_over:
                    self.show_game_result()
                else:
                    self.status_label.config(text="AI ĐANG SUY NGHĨ...", fg='#E74C3C')
                    self.root.update()
                    self.ai_thinking = True
                    self.root.after(50, self.ai_move)
    
    def ai_move(self):
        try:
            if not self.game.game_over and self.game.current_player == PLAYER_O:
                start_time = time.time()
                move = self.ai.get_best_move(self.game.board)
                elapsed = time.time() - start_time
                # Khung thống kê AI
                self.stats_label.config(
                    text=f"AI Stats | Nodes: {self.ai.nodes_visited} | "
                        f"Pruned: {self.ai.pruned_branches} | "
                        f"Time: {elapsed:.2f}s"
                )
                
                if move:
                    self.game.make_move(move[0], move[1], PLAYER_O)
                    self.draw_board()
                    
                    
                    if self.game.game_over:
                        self.show_game_result()
                    else:
                        self.status_label.config(text=f"{self.difficulty.get()} | LƯỢT CỦA BẠN (X)", fg='#F39C12')
        except Exception as e:
            print(f"Loi AI: {e}")
        finally:
            self.ai_thinking = False
    
    def show_game_result(self):
        if self.auto_reset_timer:
            self.root.after_cancel(self.auto_reset_timer)
        
        if self.game.winner == PLAYER_X:
            self.status_label.config(text="BẠN THẮNG RỒI!", fg='#27AE60')
            messagebox.showinfo("Ket thuc", "Chúc mừng! Bạn đã thắng!")
        elif self.game.winner == PLAYER_O:
            self.status_label.config(text="AI THẮNG! NHAN NEW GAME ĐỂ CHƠI TIẾP", fg='#E74C3C')
            messagebox.showinfo("Ket thuc", "Ôi không ! Bạn đã thua òi! ")
        else:
            self.status_label.config(text="HÒA!", fg='#F39C12')
            messagebox.showinfo("Ket thuc", "Hòa!")
    
    def new_game(self):
         # Hiện hộp thoại hỏi xác nhận trước khi bắt đầu ván mới
        result = messagebox.askyesno("Xac nhan", "Bạn có muốn bắt đầu ván mới?")
        if not result: #bấm No thì không làm gì
            return
        # Hỏi ai đi trước
        player_first = messagebox.askyesno(
            "Chọn người đi trước",
            "Bạn có muốn đi trước không?\n\nYes = Bạn đi trước\nNo = AI đi trước"
        )
        if self.auto_reset_timer:
            self.root.after_cancel(self.auto_reset_timer)
            
        self.game.reset()
        # Chọn độ khó
        if self.difficulty.get() == "Easy":
            depth = 2
        elif self.difficulty.get() == "Hard":
            depth = 4
        else:
            depth = 3
        self.ai = AI(depth=depth)

        self.ai_thinking = False
        self.draw_board()
        
        # Nếu người chơi đi trước
        if player_first:
            self.game.current_player = PLAYER_X
            self.status_label.config(
                   text=f"{self.difficulty.get()} | LƯỢT CỦA BẠN (X)",
                fg='#F39C12'
        )
         # Nếu AI đi trước
        else:
            self.game.current_player = PLAYER_O
            self.status_label.config(
                  text=f"{self.difficulty.get()} | AI ĐI TRƯỚC (O)",
                fg='#E74C3C'
            )
            self.root.after(300, self.ai_move)
        self.timer_label.config(text="NEW GAME! Bắt đầu nào!")
        self.root.after(2000, lambda: self.timer_label.config(text=""))
    
    def exit_game(self):
        if messagebox.askyesno("Thoat", "Bạn có muốn thoát game không?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()