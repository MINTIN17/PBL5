import socket
import threading
from flask_socketio import SocketIO
def handle_client(client_socket, addr):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
        except:
            break
        client_socket.close()
        print(f"Đã đóng kết nối với {addr}")

def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            print(f"Lỗi khi nhận tin nhắn: {e}")
            break

def send_message(client_socket):
    while True:
        try:
            message = input()
            client_socket.send(message.encode('utf-8'))
            if message == "exit":
                break
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {e}")
            break

# def broadcast(message, target_id):
#     target_socket = clients.get(target_id)
#     if target_socket:
#         try:
#             target_socket.send(message.encode('utf-8'))
#         except:
#             clients.pop(target_id, None)

def start_socket_server():
    global client_id
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12340))
    server.listen(5)
    print('Socket server started on port 12340')

    while True:
        client_socket, addr = server.accept()
        print(f'Connection from {addr}')
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()