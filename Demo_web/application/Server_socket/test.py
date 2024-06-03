from flask import Flask, render_template
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app)
@socketio.on('connect')
def test_connect():
    print('Client connected')
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
if __name__ == '__main__':
    print(1)
    socketio.run(app, host='0.0.0.0', port=8000)
