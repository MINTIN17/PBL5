import json
from flask_socketio import emit
from Demo_web.application import create_app, SocketIO

app = create_app(debug=True)
socketio = SocketIO(app)

@app.route("/")
def home():
    return "hello"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(message):
    try:
        print(message)
        # Assuming message is JSON string
        data = json.loads(message)
        print('received message: ' + str(data))
        response = f'Server received: {data["data"]}'
        emit('response', {'data': response})
    except ValueError as e:
        print(f'Error processing message: {e}')
        emit('response', {'error': 'Invalid message format'})
    
if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    # eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    app.run(debug=True)
    # socketio.run(app)

