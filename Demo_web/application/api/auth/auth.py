import os
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify, render_template, send_file

authBP = Blueprint('auth', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db
from Demo_web.application.api import account_activation

@authBP.post("/login")
def login():
    data = request.json
    if not data:
        print("loi")
    print(data)
    email = data.get("email")
    password = data.get("password")
    print(secret_key)
    try:
        user_collection = db['Users']
        if check_password(email, password, user_collection):
            user = user_collection.find_one({'Email': email})
            payload = {'user_id': str(user['_id']), 'role': user['Role']}
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return {
                "user": {
                    "User_id": str(user['_id']),
                    "Shop_name": user["Shop_name"],
                    "Password": str(user['Password']),
                    "Name": user['Name'],
                    "Image": user['image'],
                    "Email": user['Email'],
                    "Phone": user['Phone'],
                    "Address": user['Address'],
                    "Role": user['Role'],
                    "IsActivate": user['IsActivate'],
                },
                "token": token,
            }
        else:
            return jsonify({'error': "Sai tai khoan hoac mat khau"}), 401
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def register(email, password):
    shop_name = ""
    name = "user"
    phone = ""
    address = ""
    role = "user"
    image = "https://res.cloudinary.com/di53bdbjf/image/upload/v1714654040/R_vxfsuw.jpg"
    try:
        hashed_password = hash_password(password)

        user = db.Users.insert_one({
            'Shop_name': shop_name,
            'Name': name,
            'Email': email,
            "image": image,
            'Password': hashed_password,
            'Phone': phone,
            'Address': address,
            'Role': role,
            "IsActivate": 0
        }).inserted_id
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@authBP.post("/activation/<email>")
def send_code(email):
    user_collection = db['Users']
    user = user_collection.find_one({'Email': email})
    if user:
        return jsonify({'message': 'Email already exists'}), 400
    account_activation.send_mail(email)
    return "sender"

@authBP.post("/check/<email>")
def check_activation_code(email):
    data = request.json
    activation_code = data.get('activation_code')
    password = data.get('password')
    if account_activation.check_activation_code(email, activation_code) is True:
        register(email, password)
        return "register success"
    else:
        return "activation code wrong or expired", 400

@authBP.post("/reset_password/<email>")
def send_token_reset_password(email):
    account_activation.send_reset_email(email)
    return "sender"

@authBP.post("/resetpassword")
def reset_password():
    data = request.json
    new_password = data.get('new_password')
    email = data.get('email')
    db.Users.update_one(
        {
            "Email": email
        },
        {
            "$set": {
                'Password': hash_password(new_password)
            }
        }
    )
    return {
        "email": email
    }
