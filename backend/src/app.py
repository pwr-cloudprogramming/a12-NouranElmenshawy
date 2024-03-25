import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import time

backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.getenv('FRONTEND_DIR', 'frontend')

app = Flask(__name__, template_folder=frontend_dir)  
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

games = {}

@socketio.on('join')
def on_join(data):
    username = data['username']
    action = data.get('action', 'join')  
    room = data['room'] if 'room' in data else None

    if action == 'create':
        if room in games:
            emit('error', {'message': f'Room {room} already exists'})
            return
        games[room] = {'players': [username], 'board': ['' for _ in range(9)], 'turn': 'X'}
        join_room(room)
        emit('room_created', {'room': room}, broadcast=True)
        emit('game_status', {'status': 'waiting', 'players': [username], 'board': games[room]['board'], 'turn': games[room]['turn']}, room=room)
    elif room and room in games:
        join_room(room)
        game = games[room]
        if username not in game['players'] and len(game['players']) < 2:
            game['players'].append(username)
            emit('game_status', {'status': 'joined', 'players': game['players'], 'board': game['board'], 'turn': game['turn']}, room=room)
        else:
            emit('game_status', {'status': 'rejoined', 'players': game['players'], 'board': game['board'], 'turn': game['turn']}, room=room)
    else:
        emit('error', {'message': 'Room not found or not specified'})


@socketio.on('move')
def on_move(data):
    room = data['room']
    position = data['position']
    game = games[room]

    # Validate move
    if game['board'][position] == '' and game['turn'] == data['player']:
        game['board'][position] = data['player']
        winner = check_winner(game['board'])  
        
        if winner:
            game['turn'] = 'O' if game['turn'] == 'X' else 'X'
            emit('move_made', {'board': game['board'], 'turn': game['turn']}, room=room)
    
            emit('game_over', {'winner': winner}, room=room)  # Notify players of the game outcome
            # Reset the game or handle the end game scenario
            game['board'] = ['' for _ in range(9)]
            game['turn'] = 'X' if winner == 'O' else 'O'
        else:
            # No winner, continue the game
            game['turn'] = 'O' if game['turn'] == 'X' else 'X'
            emit('move_made', {'board': game['board'], 'turn': game['turn']}, room=room)


def check_winner(board):
    
    # Define the winning combinations
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
        [0, 4, 8], [2, 4, 6]              # Diagonal
    ]

    # Check for a winner
    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
            return board[combo[0]]  # Return 'X' or 'O'

    # Check for a draw
    if '' not in board:
        return 'Draw'

    return None  # No winner yet

def get_active_rooms():
    """Get a list of rooms with less than 2 players."""
    active_rooms = [room for room, game in games.items() if len(game['players']) < 2]
    return active_rooms

@socketio.on('get_active_rooms')
def handle_get_active_rooms():
    """Send a list of active rooms to the client."""
    active_rooms = get_active_rooms()
    emit('active_rooms', {'rooms': active_rooms})
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

