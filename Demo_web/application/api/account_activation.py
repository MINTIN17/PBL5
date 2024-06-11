import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import random
from time import time
import time
import threading

load_dotenv()
password_key = os.getenv('PASSWORD_KEY')
secret_key = os.getenv('SECRET_KEY')
security_password_salt = os.getenv('SECURITY_PASSWORD_SALT')
activation_data = {}
checked_tokens = []
sender_email = "webbooksw@gmail.com"
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

def generate_activation_code():
    return str(random.randint(100000, 999999))

# Hàm xác nhận mã xác minh
def is_valid_activation_code(email, activation_code):
    clean_up_expired_codes()

    if email not in activation_data:
        return False

    current_activation_code, activation_time = activation_data[email]
    current_activation_code = current_activation_code.strip()
    activation_code = str(activation_code).strip()

    print(current_activation_code)
    print(activation_code)
    if activation_code != current_activation_code or time.time() - activation_time > (2 * 60):
        return False
    return True

# Hàm gửi mã xác nhận đến mail
def send_activation_email(receiver_email, activation_code):

    password = password_key

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Kích hoạt tài khoản cho BOOK88"

    text = f"""\
    Xin chào, đây là mail được gửi từ BOOK88 để người dùng kích hoạt tài khoản.

    Bạn có thể nhập mã sau đây để kích hoạt tài khoản:
    Mã kích hoạt của bạn: {activation_code}


    Trân trọng,
    Tên của bạn"""

    html = f"""\
    <html>
      <head>
        <style>
          /* Thêm CSS tại đây */
          body {{
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            color: #333;
            margin: 0;
            padding: 0;
          }}
          .container {{
            background-color: #f9f9f9;   
            padding: 20px;    
            border-radius: 8px;    
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);       
          }}
          h1 {{
            color: #007bff;
            font-size: 24px;
          }}
          .activation-code {{
            font-size: 26px;
            font-weight: bold;
            color: #007bff;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Xin chào</h1>
          <p>Đây là mã kích hoạt của bạn:</p>
          <p class="activation-code">{activation_code}</p>
          <p>Vui lòng sử dụng mã này để kích hoạt tài khoản của bạn.</p>
          <p>Trân trọng,<br>Tên của bạn</p>
        </div>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Sử dụng máy chủ SMTP của Gmail, port 465 với SSL
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def send_mail(email):
    activation_code = generate_activation_code()
    activation_time = time.time()
    activation_data[email] = (activation_code, activation_time)
    send_activation_email(email, activation_code)

def check_activation_code(email, activation_code):
    if is_valid_activation_code(email, activation_code):
        return True
    else:
        return False


def clean_up_expired_codes():
    current_time = time.time()
    expired_emails = [email for email, (code, activation_time) in activation_data.items() if
                      current_time - activation_time > (2 * 60)]

    for email in expired_emails:
        del activation_data[email]


# Định kỳ kiểm tra và xóa mã kích hoạt hết hạn
def start_clean_up_timer():
    while True:
        clean_up_expired_codes()
        time.sleep(60)  # Kiểm tra mỗi phút

# tạo token
def generate_reset_token(email, expiration=300):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=security_password_salt)

# Hàm xác nhận token
def confirm_reset_token(token, expiration=300):
    serializer = URLSafeTimedSerializer(secret_key)
    global checked_tokens
    if token in checked_tokens:
        try:
            email = serializer.loads(token, salt=security_password_salt, max_age=expiration)
        except:
            return False
    else:
        return False
    checked_tokens.remove(token)
    return email

# Hàm gửi token reset password
def send_reset_email(to_email):
    global checked_tokens
    token = generate_reset_token(to_email)
    checked_tokens.append(token)
    reset_url = f'https://ef00-42-112-111-184.ngrok-free.app/reset_password/{token}'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = 'Đặt lại mật khẩu'

    body = f'Nhấp vào liên kết sau để đặt lại mật khẩu của bạn: {reset_url}\nLiên kết sẽ hết hạn sau 5 phút.'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, 587)
        server.starttls()
        server.login(sender_email, password_key)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print('Email đặt lại mật khẩu đã được gửi!')
    except Exception as e:
        print(f'Có lỗi xảy ra khi gửi email: {e}')

# Khởi động một thread để chạy hàm clean_up_expired_codes định kỳ
cleanup_thread = threading.Thread(target=start_clean_up_timer, daemon=True)
cleanup_thread.start()
