import os

from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
notifBP = Blueprint('notification', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@notifBP.post("/new_notif")
def notification():
    data = request.json

    receiver_id = data.get('receiver_id')
    content = data.get('content')
    isNew = 1

    try:
        nofi = db.notifications.insert_one({
            'receiver_id': ObjectId(receiver_id),
            'content': content,
            'isNew': isNew
        }).inserted_id
        return "notif success"
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@notifBP.get("/all_notif")
def notifications():
    try:
        token = request.headers.get('Authorization')
        token = utils.extract_token(token)
        print(token.get('user_id'))
        projection = {'_id': 1, 'content': 1, 'isNew': 1}
        notifications = db.notifications.find({"receiver_id": ObjectId(token.get('user_id'))}, projection)
        notifications = list(notifications)
        print(notifications)
        for notif in notifications:
            notif['_id'] = str(notif['_id'])
        return notifications
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@notifBP. put("/clear/<id>")
def clear(id):
    try:
        id = ObjectId(id)
        notification = db.notifications.find_one({"_id": id})

        if notification:
            db.notifications.update_one(
                {
                    "_id": id
                },
                {
                    "$set": {
                        'isNew': 0
                    }
                }
            )
            return "da xem thong bao"
        else:
            return jsonify({'message': 'Notif not already exists'}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@notifBP. put("/clear/all")
def clearall():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    try:
        db.notifications.update_many(
            {
                "receiver_id": ObjectId(token.get('user_id'))
            },
            {
                "$set": {
                    'isNew': 0
                }
            }
        )
        return "da xem thong bao"
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})