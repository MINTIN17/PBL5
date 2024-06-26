import os
from bson import ObjectId
from Demo_web.application import utils
from flask import Blueprint, request, jsonify
usersBP = Blueprint('users', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')
from Demo_web.application.db.db import db

@usersBP.get("/getalluser")
def GetListUser():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    count = 0
    if token.get('role') == 'admin':
        try:
            users = db['Users']
            result = users.find({'Status': 'normal'}).skip(skip).limit(limit)
            result = list(result)
            for user in result:
                count += 1
                user['_id'] = str(user['_id'])
            # print(result)
            result = utils.convert_to_json(result)
            return {
                "users": result,
                "count": count,
            }
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

@usersBP.get("/getalluserban")
def GetListUserBan():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    count = 0
    if token.get('role') == 'admin':
        try:
            users = db['Users']
            result = users.find({'Status': 'ban'}).skip(skip).limit(limit)
            result = list(result)
            for user in result:
                count += 1
                user['_id'] = str(user['_id'])
            # print(result)
            result = utils.convert_to_json(result)
            return {
                "users": result,
                "count": count,
            }
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

@usersBP.get("/<id>")
def GetUser(id):
    try:
        id = ObjectId(id)
        result = db.Users.find_one({"_id": id})
        result['_id'] = str(result['_id'])
        result['Password'] = None
        # print(result)
        result = utils.convert_to_json(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@usersBP.put("/<id>")
def UpdateUser(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    if token.get('role') == 'admin' or token.get('user_id') == id:
        data = request.json
        id = ObjectId(id)
        try:
            name = data.get('Name')
            phone = data.get('Phone')
            address = data.get('Address')
            image = data.get('image')

            user = db.Users.find_one({'_id': id})
            if user:
                db.Users.update_one(
                    {
                        "_id": id
                    },
                    {
                        "$set": {
                            'Name': name,
                            'Phone': phone,
                            'Address': address,
                            'image': image
                        }
                    }
                )
                user = db.Users.find_one({'_id': id})
                user['_id'] = str(user['_id'])
                user = utils.convert_to_json(user)
                return user
            else:
                return jsonify({'message': 'User not already exists'}), 400
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

# @usersBP.delete("/<id>")
# def DeleteUser(id):
#     token = request.headers.get('Authorization')
#     token = utils.extract_token(token)
#     if token.get('role') == 'admin':
#         id = ObjectId(id)
#         try:
#             result = db.Users.delete_one({'_id': id})
#
#             # Xóa sách
#             books = db.Users.find({'SellerId': id})
#             for book in books:
#                 result = db.books.delete_one({'_id': book['_id']})
#             # Xóa cart
#             carts = db.Carts.find({'user_id': id})
#             for cart in carts:
#                 result = db.Carts.delete_one({'_id': cart['_id']})
#             # Xóa discount
#             discounts = db.Discounts.find({'ShopId': id})
#             for discount in discounts:
#                 result = db.Discounts.delete_one({'_id': discount['_id']})
#             # Xóa conversation
#             list_conversation = db.Conversations.find({
#                 "$or": [
#                     {"user_id_1": id},
#                     {"user_id_2": id}
#                 ]
#             })
#             for conversation in list_conversation:
#                 # Xóa message
#                 messages = db.Messages.find({'conversationId': conversation['_id']})
#                 for message in messages:
#                     result = db.Messages.delete_one({'_id': message['_id']})
#                 result = db.Conversations.delete_one({'_id': conversation['_id']})
#
#
#
#             if result.deleted_count == 1:
#                 return f"User with _id {str(id)} has been deleted successfully."
#             else:
#                 return f"User with _id {str(id)} not found."
#         except Exception as e:
#             return jsonify({"error": str(e)})
#     else:
#         return jsonify({"message": "khong du quyen han"})

@usersBP.put("/ban/<id>")
def Ban_user(id):
    id = ObjectId(id)
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    try:
        if token.get('role') == 'admin':
            result = db.Users.update_one({'_id': id}, {"$set": {'Status': 'ban',}})
            return f"User with _id {str(id)} has been ban successfully."
        else:
            return "khong du quyen han"
    except Exception as e:
        return jsonify({"error": str(e)})

@usersBP.put("/unban/<id>")
def Unban_user(id):
    id = ObjectId(id)
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    try:
        if token.get('role') == 'admin':
            result = db.Users.update_one({'_id': id}, {"$set": {'Status': 'normal', }})
            return f"User with _id {str(id)} has been unban successfully."
        else:
            return "khong du quyen han"
    except Exception as e:
        return jsonify({"error": str(e)})

@usersBP.get("/role/<role_account>")
def GetUserByRole(role_account):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit

    if token.get('role') == 'admin':
        if role_account == 'admin':
            try:
                users = db['Users'].find({"Role": "admin"}).skip(skip).limit(limit)
                users = list(users)
                for user in users:
                    user['_id'] = str(user['_id'])
                # print(result)
                result = utils.convert_to_json(users)
                return {
                    "admin": result,
                    "count": db.Users.count_documents({"Role": "admin"}),
                }
            except Exception as e:
                return jsonify({"error": str(e)})
        if role_account == 'seller':
            try:
                users = db['Users'].find({"Role": "seller", "Status": "normal"}).skip(skip).limit(limit)
                users = list(users)
                for user in users:
                    user['_id'] = str(user['_id'])
                # print(result)
                result = utils.convert_to_json(users)
                return {
                    "seller": result,
                    "count": db.Users.count_documents({"Role": "seller"}),
                }
            except Exception as e:
                return jsonify({"error": str(e)})
        else:
            try:
                users = db['Users'].find({"Role": "user", "Status": "normal"}).skip(skip).limit(limit)
                users = list(users)
                for user in users:
                    user['_id'] = str(user['_id'])
                # print(result)
                result = utils.convert_to_json(users)
                return {
                    "users": result,
                    "count": db.Users.count_documents({"Role": "user"}),
                }
            except Exception as e:
                return jsonify({"error": str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

@usersBP.post("/uprole")
def Up_Role():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    data = request.json
    shopname = data.get('shopname')
    try:
        db.Users.update_one({
            "_id": ObjectId(token.get('user_id'))
        },
            {
                "$set": {
                    'Role': 'seller',
                    'Shop_name': shopname
                }
            }
        )
        return "uprole success"
    except Exception as e:
        return jsonify({"error": str(e)})

@usersBP.get("/books")
def GetBook_PageByUser():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    skip = (page - 1) * limit

    # Tính tổng số lượng sách của người bán (SellerId)
    total_books_count = db.books.count_documents({"SellerId": ObjectId(token.get('user_id'))})

    # Kiểm tra nếu skip vượt quá tổng số sách có sẵn
    if skip >= total_books_count:
        return {
            "books": [],
            "count": total_books_count
        }

    # Thực hiện truy vấn MongoDB với phân trang và giới hạn số lượng kết quả
    books = db.books.find({"SellerId": ObjectId(token.get('user_id'))}).skip(skip).limit(limit)
    books = list(books)
    print(books)
    # Xử lý kết quả trả về
    for book in books:
        book['_id'] = str(book['_id'])
        user = db.Users.find_one({"_id": book['SellerId']})
        genre = db.Genres.find_one({"_id": book['Genre']})
        print(genre)
        shop_name = user['Shop_name']
        book['Genre'] = genre['Theloai']
        del book['SellerId']
        book['shop_name'] = shop_name

    return {
        "books": books,
        "count": total_books_count
    }



