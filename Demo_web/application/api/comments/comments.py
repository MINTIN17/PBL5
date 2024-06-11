import os
from datetime import datetime

from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
commentBP = Blueprint('comment', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db


@commentBP.get("/book/<id>")
def GetCommnet_Book(id):
    try:
        comments = db['comments']
        parent_comments = comments.find({"book_id": ObjectId(id), "parent_comment_id": None}).sort("_id")
        CommnetOfBook = []
        for parent_comment in parent_comments:
            like = []
            dislike = []
            user = db.Users.find_one({"_id": parent_comment['user_id']})
            if user:
                parent_comment['user_name'] = user['Name']
            parent_comment['book_id'] = str(parent_comment['book_id'])
            parent_comment['user_id'] = str(parent_comment['user_id'])
            parent_comment['parent_comment_id'] = str(parent_comment['parent_comment_id']) if parent_comment[
                'parent_comment_id'] else None
            parent_comment['_id'] = str(parent_comment['_id'])
            parent_comment['like_count'] = len(parent_comment['like'])
            parent_comment['dislike_count'] = len(parent_comment['dislike'])
            for user in parent_comment['like']:
                like.append(str(user))
            parent_comment['like'] = like
            for user in parent_comment['dislike']:
                dislike.append(str(user))
            parent_comment['dislike'] = dislike
            replies = comments.find({"parent_comment_id": ObjectId(parent_comment['_id'])})
            replies = list(replies)
            rep = []
            for reply in replies:
                reply_like = []
                reply_dislike = []
                for user in reply['like']:
                    reply_like.append(str(user))
                for user in reply['dislike']:
                    reply_dislike.append(str(user))
                user_name_reply = db.Users.find_one({"_id": reply['user_id']})
                if user_name_reply:
                    reply['username'] = user_name_reply['Name']
                reply['_id'] = str(reply['_id'])
                reply['book_id'] = str(reply['book_id'])
                reply['user_id'] = str(reply['user_id'])
                reply['parent_comment_id'] = str(reply['parent_comment_id'])
                reply['like_count'] = len(reply['like'])
                reply['dislike_count'] = len(reply['dislike'])
                reply['like'] = reply_like
                reply['dislike'] = reply_dislike
                rep.append(reply)
            parent_comment['replies'] = rep
            CommnetOfBook.append(parent_comment)
        return jsonify(CommnetOfBook)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})

@commentBP.post("/create")
def Post_Comment():
    data = request.json
    print(1)
    book_id = data.get('book_id')
    user_id = data.get('user_id')
    content = data.get('content')
    parent_comment_id = data.get('parent_comment_id')
    if parent_comment_id is not None:
        parent_comment_id = ObjectId(parent_comment_id)
    else:
        parent_comment_id = None
    try:
        current_time = datetime.now()
        comment = db.comments.insert_one({
            'book_id': ObjectId(book_id),
            'user_id': ObjectId(user_id),
            'content': content,
            'timestamp': current_time,
            'parent_comment_id': parent_comment_id,
            'like': [],
            'dislike': [],
        }).inserted_id
        return "post success"
    except Exception as e:
        return jsonify({"error": str(e)})

@commentBP.put("/<id>")
def Edit_Comment(id):
    data = request.json
    content = data.get('content')
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    try:
        cmt = db.comments.find_one({"_id": ObjectId(id)})
        if token.get('user_id') == str(cmt['user_id']):
            db.comments.update_one(
                {
                    "_id": ObjectId(id)
                },
                {
                    "$set": {
                        'content': content
                    }
                }
            )
            return "edit comment success"
        else:
            return "error"
    except Exception as e:
        return jsonify({"error": str(e)})

@commentBP.delete("/<id>")
def Delete_Comment(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    try:
        cmt = db.comments.find_one({"_id": ObjectId(id)})
        if token.get('user_id') == str(cmt['user_id']):
            if cmt['parent_comment_id'] is not None:
                result = db.comments.delete_one({'_id': cmt['_id']})
            else:
                comments = db.comments.find({"parent_comment_id": ObjectId(id)})
                for comment in comments:
                    result = db.comments.delete_one({'_id': comment['_id']})
                result = db.comments.delete_one({'_id': cmt['_id']})
            if result.deleted_count == 1:
                return f"Comment with _id {id} has been deleted successfully."
            else:
                return f"Comment with _id {id} not found."
        return "error"
    except Exception as e:
        return jsonify({"error": str(e)})


@commentBP.put("/like/<id>")
def Like(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    try:
        if token:
            comment_id = ObjectId(id)
            user_id = ObjectId(token.get('user_id'))
            comment = db.comments.find_one({"_id": comment_id})
            if user_id in comment['like']:
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$pull": {
                            'like': user_id
                        }
                    }
                )
                print(1)
                return "unlike success"
            elif user_id in comment['dislike']:
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$push": {
                            'like': user_id
                        }
                    }
                )
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$pull": {
                            'dislike': user_id
                        }
                    }
                )
                print(2)
                return "like success and undislike"
            else:
                result = db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$push": {
                            'like': user_id
                        }
                    }
                )
                print(3)
                print(result.modified_count)
                return "like success"
        return "login da ban ei"
    except Exception as e:
        return jsonify({"error": str(e)})

@commentBP.put("/dislike/<id>")
def Dislike(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    try:
        if token:
            comment_id = ObjectId(id)
            user_id = ObjectId(token.get('user_id'))
            comment = db.comments.find_one({"_id": comment_id})
            if user_id in comment['dislike']:
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$pull": {
                            'dislike': user_id
                        }
                    }
                )
                return "undislike success"
            elif user_id in comment['like']:
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$push": {
                            'dislike': user_id
                        }
                    }
                )
                db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$pull": {
                            'like': user_id
                        }
                    }
                )
                return "dislike success and unlike"
            else:
                result = db.comments.update_one(
                    {
                        "_id": comment_id
                    },
                    {
                        "$push": {
                            'dislike': user_id
                        }
                    }
                )
                print(result.modified_count)
                return "dislike success"
        return "login da ban ei"
    except Exception as e:
        return jsonify({"error": str(e)})


