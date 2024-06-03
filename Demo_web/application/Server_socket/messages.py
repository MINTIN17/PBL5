import socketio

# Tạo một client Socket.IO
sio = socketio.Client()

# Khi client kết nối thành công đến máy chủ
@sio.event
def connect():
    print('Kết nối thành công!')

# Khi client nhận được một sự kiện 'message' từ máy chủ
@sio.on('message')
def on_message(data):
    print('Nhận được thông điệp từ máy chủ:', data)

# Khi có lỗi xảy ra trong quá trình kết nối
@sio.event
def error(err):
    print("Lỗi:", err)

# Kết nối đến máy chủ
sio.connect('ws://0.tcp.ap.ngrok.io:18288/')

# Gửi một tin nhắn đến máy chủ
sio.emit('message', 'Xin chào từ client Python!')

# Lắng nghe sự kiện từ máy chủ
sio.wait()
