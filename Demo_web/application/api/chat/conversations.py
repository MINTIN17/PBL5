import os

from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
conversationBP = Blueprint('conversation', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@conversationBP.get("/conversations")
def ListConversation():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    user_id = ObjectId(token.get('user_id'))
    list_conversation = db.Conversations.find({
        "$or": [
            {"user_id_1": user_id},
            {"user_id_2": user_id}
        ]
    })

    user_ids = set()
    for conversation in list_conversation:
        if conversation["user_id_1"] != user_id:
            user_ids.add(conversation["user_id_1"])
        if conversation["user_id_2"] != user_id:
            user_ids.add(conversation["user_id_2"])
    users = db.Users.find({"_id": {"$in": list(user_ids)}})
    list_user = [{"user_id": str(user["_id"]), "name": user["Name"], "image": user["image"]} for user in users]
    return list_user
@conversationBP.post("/load")
def conversation():
    data = request.json
    senderId = ObjectId(data.get('senderId'))
    receiverId = ObjectId(data.get('receiverId'))
    conversation = db.Conversations.find_one({"user_id_1": senderId, "user_id_2": receiverId})
    if conversation is None:
        conversation = db.Conversations.find_one({"user_id_1": receiverId, "user_id_2": senderId})
    if conversation is None:
        return "null"
    else:
        try:
            messages = db.Messages.find({"conversationId": conversation['_id']})
            messages = list(messages)
            for message in messages:
                del message['conversationId']
                message['_id'] = str(message['_id'])
                message['senderId'] = str(message['senderId'])
                message['receiverId'] = str(message['receiverId'])
            return messages
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'error': str(e)})


