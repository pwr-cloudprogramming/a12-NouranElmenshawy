import os
import json
import boto3
import requests  # Added import for requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from auth_service import register_user, confirm_user, login_user
from flask_socketio import SocketIO, emit, join_room
from botocore.exceptions import ClientError

REGION = 'us-east-1'

backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.getenv('FRONTEND_DIR', 'frontend')
# frontend_dir = os.path.join(backend_dir, '..', '..', 'frontend', 'src')

app = Flask(__name__, template_folder=frontend_dir)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    response = register_user(data['username'], data['password'], data['email'])
    return jsonify(response)

@app.route('/api/confirm', methods=['POST'])
def confirm():
    data = request.get_json()
    response = confirm_user(data['username'], data['code'])
    return jsonify(response)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    response = login_user(data['username'], data['password'])
    return jsonify(response)

@app.route('/api/submit_game_result', methods=['POST'])
def submit_game_result():
    data = request.get_json()
    
    # Log the incoming request data
    print("Received data:", data)
    
    required_fields = ['game_id', 'player1', 'player2', 'winner']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Call the Lambda function
    lambda_client = boto3.client('lambda', region_name=REGION)
    try:
        response = lambda_client.invoke(
            FunctionName='UpdateRanking',
            InvocationType='RequestResponse',
            Payload=json.dumps(data)
        )
        response_payload = json.loads(response['Payload'].read())
        print("Lambda response:", response_payload)
        
        if response['StatusCode'] != 200:
            return jsonify({'error': 'Lambda function invocation failed'}), 500
        
        return jsonify(response_payload)
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

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
    room = data.get('room')
    position = data.get('position')
    player = data.get('player')

    if not room or room not in games:
        emit('error', {'message': 'Room not found or not specified'})
        return

    game = games[room]

    # Validate move
    if game['board'][position] == '' and game['turn'] == player:
        game['board'][position] = player
        winner_symbol = check_winner(game['board'])

        if winner_symbol:
            winner_name = game['players'][0] if winner_symbol == 'X' else game['players'][1]
            emit('move_made', {'board': game['board'], 'turn': game['turn']}, room=room)
            emit('game_over', {'winner': winner_name}, room=room)
            # Store game result and notify via API
            try:
                response = requests.post(
                    'https://sl8bv9ikyi.execute-api.us-east-1.amazonaws.com/prod/submit_game_result',
                    json={
                        'game_id': room,
                        'player1': game['players'][0],
                        'player2': game['players'][1],
                        'winner': winner_name
                    }
                )
                if response.status_code != 200:
                    print(f"Failed to submit game result: {response.text}")
            except Exception as e:
                print(f"Error submitting game result: {str(e)}")

            # Reset the game or handle the end game scenario
            game['board'] = ['' for _ in range(9)]
            game['turn'] = 'X' if winner_symbol == 'O' else 'O'
        else:
            game['turn'] = 'O' if game['turn'] == 'X' else 'X'
            emit('move_made', {'board': game['board'], 'turn': game['turn']}, room=room)

def check_winner(board):
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
        [0, 4, 8], [2, 4, 6]              # Diagonal
    ]

    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
            return board[combo[0]]  # Return 'X' or 'O'
    
    if '' not in board:
        return 'Draw'
    
    return None  # No winner yet

def get_active_rooms():
    active_rooms = [room for room, game in games.items() if len(game['players']) < 2]
    return active_rooms

@socketio.on('get_active_rooms')
def handle_get_active_rooms():
    active_rooms = get_active_rooms()
    emit('active_rooms', {'rooms': active_rooms})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
