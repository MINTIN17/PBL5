from flask import Flask, request, Blueprint
from flask_socketio import SocketIO, send, emit
from Demo_web.application import socketio
clients = {}  # Dictionary to store connected WebSocket clients with their IDs





@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    disconnected_client_id = None
    for client_id, socket in clients.items():
        if socket == request.sid:
            disconnected_client_id = client_id
            break
    if disconnected_client_id:
        del clients[disconnected_client_id]

@socketio.on('message')
def handle_message(data):
    print('Received message: ', data)
    parsed_message = data

    if parsed_message.get('type') == 'clientId':
        client_id = parsed_message.get('clientId')
        print("id: " + client_id)
        clients[client_id] = request.sid  # Store the WebSocket connection with the client's ID

    elif parsed_message.get('type') == 'privateMessage':
        print(parsed_message.get('content'))
        recipient_id = parsed_message.get('recipientId')
        sender_id = parsed_message.get('senderId')
        recipient_sid = clients.get(recipient_id)
        sender_sid = clients.get(sender_id)

        if recipient_sid:
            emit('message', parsed_message, room=recipient_sid)  # Forward the message to the recipient
        else:
            print(f"Recipient with ID {recipient_id} is not available.")

        if sender_sid:
            emit('message', parsed_message, room=sender_sid)  # Forward the message to the sender as a confirmation
        else:
            print(f"Sender with ID {sender_id} is not available.")


