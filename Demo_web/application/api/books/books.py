import os
import urllib
from datetime import datetime
from urllib import parse

import pytz
from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
booksBP = Blueprint('books', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@booksBP.get("/getallbook")
def GetListBooks():
    try:
        List_books = db.books.aggregate([
            {
                "$lookup": {
                    "from": "Users",
                    "localField": "SellerId",
                    "foreignField": "_id",
                    "as": "Seller"
                }
            },
            {
                "$unwind": "$Seller"
            },
            {
                "$match": {
                    "Seller.Status": "normal"
                }
            },
            {
                "$lookup": {
                    "from": "Genres",
                    "localField": "Genre",
                    "foreignField": "_id",
                    "as": "genre"
                }
            },
            {
                "$unwind": "$genre"
            },
            {
                "$group": {
                    "_id": {"$toString": "$_id"},
                    "title": {"$first": "$Title"},
                    "genre": {"$first": "$genre.Theloai"},
                    "description": {"$first": "$Description"},
                    "quantity": {"$first": "$Quantity"},
                    "price": {"$first": "$Price"},
                    "AuthorName": {"$first": "$AuthorName"},
                    "PublisherName": {"$first": "$PublisherName"},
                    "image": {"$first": "$image"},
                    "Sellers": {"$first": "$Seller.Name"}  # Tạo một mảng các tên Seller
                }
            },
            {
                "$sort": {"_id": 1}  # Sắp xếp tăng dần theo _id
            }
        ])
        List_books = list(List_books)
        return (List_books)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@booksBP.get("/gettopbook")
def GetTopBooks():
    try:
        List_books = db.books.aggregate([
            {
                "$lookup": {
                    "from": "Users",
                    "localField": "SellerId",
                    "foreignField": "_id",
                    "as": "Seller"
                }
            },
            {
                "$unwind": "$Seller"
            },
            {
                "$match": {
                    "Seller.status": "normal"
                }
            },
            {
                "$lookup": {
                    "from": "Genres",
                    "localField": "Genre",
                    "foreignField": "_id",
                    "as": "genre"
                }
            },
            {
                "$unwind": "$genre"
            },
            {
                "$group": {
                    "_id": {"$toString": "$_id"},
                    "title": {"$first": "$Title"},
                    "genre": {"$first": "$genre.Theloai"},
                    "description": {"$first": "$Description"},
                    "quantity": {"$first": "$Quantity"},
                    "price": {"$first": "$Price"},
                    "AuthorName": {"$first": "$AuthorName"},
                    "PublisherName": {"$first": "$PublisherName"},
                    "image": {"$first": "$image"},
                    "Sellers": {"$first": "$Seller.Name"},
                    "Sales_quantity": {"$first": "$Sales_quantity"}
                }
            },
            {
                "$sort": {"Sales_quantity": -1}  # Sắp xếp giảm dần theo Sales_quantity
            },
            {
                "$limit": 20  # Giới hạn số lượng kết quả là 20
            }
        ])
        List_books = list(List_books)
        return (List_books)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@booksBP.get("/<id>")
def GetBookById(id):
    try:
        id = ObjectId(id)
        try:
            book = db.books.find_one({"_id": id})
            user = db.Users.find_one({"_id": book['SellerId']})
            genre = db.Genres.find_one({"_id": book['Genre']})
            shop_name = user['Shop_name']
            book['SellerId'] = str(book['SellerId'])
            book['Genre'] = genre['Theloai']
            book['Seller_name'] = shop_name
            book['_id'] = str(book['_id'])
            return book
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        return jsonify({"error": str(e)})

@booksBP.get("/author_name/<author_name>")
def GetBookByAuthorName(author_name):
    try:
        decoded_author_name = urllib.parse.unquote(author_name)
        books = db.books.find({"AuthorName": decoded_author_name})

        books = list(books)
        list_book = []
        for book in books:
            user = db.Users.find_one({"_id": book['SellerId']})
            if user['Status'] == 'ban':
                books.remove(book)
            else:
                genre = db.Genres.find_one({"_id": book['Genre']})
                shop_name = user['Shop_name']
                book['shop_name'] = shop_name
                book['Genre'] = genre['Theloai']
                book['_id'] = str(book['_id'])
                del book['SellerId']
                list_book.append(book)
        return list_book
    except Exception as e:
        return jsonify({"error": str(e)})

@booksBP.get("/genre")
def GetGenreOfBook():
    genres = db.Genres.find({})
    genres = list(genres)
    for genre in genres:
        genre['_id'] = str(genre['_id'])
    return genres

@booksBP.get("/genre/<genre>")
def GetBookByGenre(genre):
    try:
        decoded_genre = urllib.parse.unquote(genre)
        genre = db.Genres.find_one({"Theloai": decoded_genre})
        books = db.books.find({"Genre": genre['_id']})
        books = list(books)
        list_books = []
        for book in books:
            user = db.Users.find_one({"_id": book['SellerId']})
            if user['Status'] == 'ban':
                books.remove(book)
            else:
                genre = db.Genres.find_one({"_id": book['Genre']})

                shop_name = user['Shop_name']
                book['Genre'] = genre['Theloai']
                book['_id'] = str(book['_id'])
                del book['SellerId']
                book['shop_name'] = shop_name
                list_books.append(book)
        return list_books
    except Exception as e:
        return jsonify({"error": str(e)})

@booksBP.get("/shop/<id>")
def GetBookOfSeller(id):
    books = db.books.find({"SellerId": ObjectId(id)})
    books = list(books)

    for book in books:
        book["_id"] = str(book["_id"])
        user = db.Users.find_one({"_id": book['SellerId']})
        genre = db.Genres.find_one({"_id": book['Genre']})

        shop_name = user['Shop_name']
        book['Genre'] = genre['Theloai']
        book['_id'] = str(book['_id'])
        del book['SellerId']
        book['shop_name'] = shop_name
    return {"books": books,
            "count": len(books)
            }

@booksBP.get("/books")
def GetBook_Page():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit

    # Thực hiện truy vấn MongoDB với phân trang và giới hạn số lượng kết quả
    books = db.books.find().skip(skip).limit(limit)
    books = list(books)
    list_book = []
    # Chuyển đổi kết quả trả về thành danh sách các đối tượng
    for book in books:
        book['_id'] = str(book['_id'])
        user = db.Users.find_one({"_id": book['SellerId']})
        genre = db.Genres.find_one({"_id": book['Genre']})
        shop_name = user['Shop_name']
        book['Genre'] = genre['Theloai']
        del book['SellerId']
        book['shop_name'] = shop_name
        if user['Status'] == 'normal':
            list_book.append(book)
    books = list(books)
    return {
        "books": list_book,
        "count": len(list_book),
    }


@booksBP.post("/create")
def Create_book():
    try:
        token = request.headers.get('Authorization')
        token = utils.extract_token(token)

        if token.get('role') == 'seller':
            data = request.json
            current_timestamp = datetime.now()

            title = data.get('title')
            genre = data.get('genre')
            description = data.get('description')
            quantity = data.get('quantity')
            price = data.get('price')
            seller_id = ObjectId(token.get('user_id'))
            author_name = data.get('author_name')
            publisher_name = data.get('publisher_name')
            image = data.get('image')
            time_create = current_timestamp
            book = db.books.insert_one({
                'Title': title,
                'Genre': ObjectId(genre),
                'Description': description,
                "Quantity": quantity,
                'Price': price,
                'SellerId': seller_id,
                'AuthorName': author_name,
                'PublisherName': publisher_name,
                "image": image,
                "time_create": time_create,
                "Sales_quantity": 0
            }).inserted_id

            return "create new book success"

    except Exception as e:
        return jsonify({"error": str(e)})

@booksBP.delete("/<id>")
def DeleteBook(id):
    token = request.headers.get('Authorization')
    token = utils.extract_token(token)
    print(token)
    book = db.books.find_one({"_id": ObjectId(id)})
    print(book)
    if token.get('user_id') == str(book['SellerId']) or token.get('role') == 'admin':
        try:
            result = db.books.delete_one({'_id': ObjectId(id)})

            if result.deleted_count == 1:
                return f"Book with _id {str(id)} has been deleted successfully."
            else:
                return f"Book with _id {str(id)} not found."
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"message": "khong du quyen han"})

@booksBP.put("/<id>")
def Update_book(id):
    try:
        token = request.headers.get('Authorization')
        token = utils.extract_token(token)
        book = db.books.find_one({"_id": ObjectId(id)})
        if token.get('role') == 'admin' or token.get('user_id') == str(book['SellerId']):
            data = request.json

            title = data.get('title')
            genre = data.get('genre')
            description = data.get('description')
            quantity = data.get('quantity')
            price = data.get('price')
            seller_id = ObjectId(token.get('user_id'))
            author_name = data.get('author_name')
            publisher_name = data.get('publisher_name')
            image = data.get('image')

            db.books.update_one(
                {
                    "_id": ObjectId(id)
                },
                {
                    "$set": {
                        'Title': title,
                        'Genre': ObjectId(genre),
                        'Description': description,
                        "Quantity": quantity,
                        'Price': price,
                        'SellerId': seller_id,
                        'AuthorName': author_name,
                        'PublisherName': publisher_name,
                        "image": image
                    }
                }
            )
            return "update book success"
        return "Khong du quyen han"
    except Exception as e:
        return jsonify({"error": str(e)})


@booksBP.get("/fix")
def fix():
    try:
        # specific_datetime = datetime(2024, 5, 3, 9, 28, 57, 652000, tzinfo=pytz.utc)
        result = db.Users.update_many({}, {"$unset": {"IsActivate": ""}})
        # Define the new attribute
        # new_attribute = {
        #     'condition': 0
        # }
        # result = db.Discounts.update_many({}, {"$set": new_attribute})
        return "fix ok"
    except Exception as e:
        return jsonify({"error": str(e)})