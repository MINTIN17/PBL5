import os
import bcrypt
import jwt
from bson import ObjectId
from dotenv import load_dotenv
from Demo_web.application.db.db import db

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
secret_key = os.getenv('SECRET_KEY')


def check_password(email, password, users_collection):
    user = users_collection.find_one({'Email': email})
    if user:
        # Trích xuất chuỗi băm mật khẩu đã lưu từ cơ sở dữ liệu
        hashed_password = user['Password']

        # So sánh mật khẩu nhập vào với chuỗi băm đã lưu
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
        else:
            return False
    else:
        return False


def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


def extract_token(token):
    try:
        token = token.split(" ")[1]
        # token = token[7:]
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        id = ObjectId(decoded_token["user_id"])
        user = db.Users.find_one({'_id': id})
        if user:
            return decoded_token
        else:
            return 1
    except jwt.ExpiredSignatureError:
        # Xử lý token hết hạn
        return 2
    except jwt.InvalidTokenError:
        # Xử lý token không hợp lệ
        return 3


def convert_to_json(data):
    if isinstance(data, bytes):
        return data.decode('utf-8')  # Chuyển đổi bytes thành chuỗi Unicode
    elif isinstance(data, list):
        return [convert_to_json(item) for item in data]  # Chuyển đổi từng phần tử trong danh sách
    elif isinstance(data, dict):
        return {key: convert_to_json(value) for key, value in
                data.items()}  # Chuyển đổi từng cặp key-value trong từ điển
    else:
        return data  # Trường hợp còn lại không cần xử lý


def Total_Funds(money, discount):
    if discount['DiscountAmount'] == 0:
        total_funds = money - money / 100 * discount['DiscountPercent']
    else:
        total_funds = money - discount['DiscountAmount']
    return total_funds
