from flask import Flask, render_template, request, jsonify
from AI import AI
import os

app = Flask(__name__)

# Khởi tạo AI
ai_player = AI()

@app.route('/')
def index():
    return "Giao diện Caro đang sẵn sàng!"

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    # Lấy ma trận bàn cờ từ request
    board = data.get('board') 
    
    if not board:
        return jsonify({"error": "Board data is missing"}), 400
    
    # Gọi AI tính toán nước đi
    best_move = ai_player.get_best_move(board)
    
    if best_move:
        # Trả về tọa độ hàng và cột cho Frontend
        return jsonify({
            "row": best_move[0],
            "col": best_move[1]
        })
    
    return jsonify({"error": "No move found"}), 404

# Lưu ý: Vercel sẽ tự gọi đối tượng 'app', không cần app.run()