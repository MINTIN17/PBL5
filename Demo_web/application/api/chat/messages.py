import os

from bson import ObjectId

from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
messagesBP = Blueprint('messages', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@messagesBP.post("/send")
def messages():
    data = request.json
    senderId = ObjectId(data.get('senderId'))
    receiverId = ObjectId(data.get('receiverId'))
    content = data.get('content')
    SentTime = data.get('SentTime')
    conversation = db.Conversations.find_one({"user_id_1": senderId, "user_id_2": receiverId})
    if conversation is None:
        conversation = db.Conversations.find_one({"user_id_1": receiverId, "user_id_2": senderId})
    try:
        if conversation:
            message = db.Messages.insert_one({
                "conversationId": ObjectId(conversation['_id']),
                "senderId": senderId,
                "receiverId": receiverId,
                "content": content,
                "SentTime": SentTime
            }).inserted_id
            return "messages success"
        else:
            conversation = db.Conversations.insert_one({
                "user_id_1": senderId,
                "user_id_2": receiverId
            }).inserted_id
            message = db.Messages.insert_one({
                "conversationId": ObjectId(conversation),
                "senderId": senderId,
                "receiverId": receiverId,
                "content": content,
                "SentTime": SentTime
            }).inserted_id
            return "create conversation and messages success"
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})


