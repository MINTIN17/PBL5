import os

from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
cartBP = Blueprint('cart', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@cartBP.get("/self")
def User_Cart():
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    if token.get('role') == 'admin':
        return []
    try:
        cart = db.Carts.aggregate([
            {"$match": {"user_id": ObjectId(token.get('user_id'))}},
            {
                "$lookup": {
                    "from": "books",
                    "localField": "book_id",
                    "foreignField": "_id",
                    "as": "book"
                }
            },
            {"$unwind": "$book"},
            {
                "$lookup": {
                    "from": "Users",
                    "localField": "book.SellerId",
                    "foreignField": "_id",
                    "as": "seller"
                }
            },
            {"$unwind": "$seller"},
            {
                "$match": {
                    "book": {"$ne": []},
                    "seller": {"$ne": []}
                }
            },
            {
                "$addFields": {
                    "sellerIdString": {"$toString": "$book.SellerId"},
                    "bookIdString": {"$toString": "$book._id"}
                }
            },
            {
                "$group": {
                    "_id": {"$toString": "$book.SellerId"},
                    "shop_id": {"$first": "$sellerIdString"},
                    "shop_name": {"$first": "$seller.Shop_name"},
                    "books": {
                        "$push": {
                            "_id": {"$toString": "$book._id"},
                            "title": "$book.Title",
                            "price": "$book.Price",
                            "quantity": "$quantity",
                            "cart_id": {"$toString": "$_id"},
                            "image": "$book.image",
                            "shop_id": {"$toString": "$book.SellerId"},
                            "total_price": {
                                "$multiply": [
                                    {"$toInt": "$book.Price"},
                                    {"$toInt": "$quantity"}
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "shop_id": 1,
                    "shop_name": 1,
                    "books": 1
                }
            },
            {"$sort": {"shop_id": 1}}
        ])
        cart =list(cart)
        print(cart)

        return cart
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@cartBP.post("/<id>")
def AddToCart(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    book_id = ObjectId(id)
    data = request.json
    user_id = ObjectId(token.get('user_id'))
    quantity = data.get("quantity")

    cart = db.Carts.find_one({"book_id": book_id, "user_id": user_id})
    if cart:
        db.Carts.update_one(
            {
                "_id": cart['_id']
            },
            {
                "$set": {
                    'quantity': cart['quantity'] + quantity,
                }
            }
        )
        return "add quantity of book to cart success"
    else:
        try:
            cart = db.Carts.insert_one({
                'book_id': book_id,
                'user_id': user_id,
                'quantity': quantity,
            }).inserted_id
            return "add book to cart success"
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'error': str(e)})

@cartBP.put("/<id>")
def UpdateCart(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    data = request.json
    cart = db.Carts.find_one({"_id": ObjectId(id)})
    if token.get('user_id') == str(cart['user_id']):
        quantity = data.get("quantity")
        print(quantity)
        try:
            db.Carts.update_one(
                {
                    "_id": ObjectId(id)
                },
                {
                    "$set": {
                        'quantity': quantity,
                    }
                }
            )
            return "update cart success"
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

@cartBP.delete("/<id>")
def DeleteCart(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)

    cart = db.Carts.find_one({"_id": ObjectId(id)})
    if token.get('user_id') == str(cart['user_id']):
        try:
            result = db.Carts.delete_one({'_id': ObjectId(id)})

            if result.deleted_count == 1:
                return f"Cart with _id {str(id)} has been deleted successfully."
            else:
                return f"Cart with _id {str(id)} not found."

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})


