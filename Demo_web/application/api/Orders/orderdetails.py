from bson import ObjectId
from flask import Blueprint, request, jsonify
from Demo_web.application.db.db import db

orderDetailBP = Blueprint('order_detail', __name__)

# user
@orderDetailBP.route('/order_detail/<user_id>', methods=['GET'])
def get_order_detail_by_user(user_id):
    try:
        user_id = ObjectId(user_id)

        # Truy vấn cơ sở dữ liệu để lấy danh sách các đơn hàng của người dùng
        order_details = db.OrderDetails.find({'UserId': user_id})

        # Biến đổi kết quả thành một danh sách JSON
        order_details_list = []
        for order_detail in order_details:
            # Lấy danh sách ID sách, số lượng và giá từ các trường mảng trong đối tượng JSON
            book_ids = order_detail['BookId']
            quantities = order_detail['Quantity']
            prices = order_detail['Price']

            # Tạo danh sách các mặt hàng trong đơn hàng
            items = []
            for i in range(len(book_ids)):
                book_id = book_ids[i]
                # Truy vấn thông tin chi tiết của sách từ cơ sở dữ liệu
                book_detail = db.books.find_one({"_id": ObjectId(book_id)}, {'_id': 0, 'Title': 1, 'image': 1, 'Genre': 1})
                genre = db.Genres.find_one({"_id": book_detail['Genre']})
                item = {
                    'BookId': str(book_id),
                    'Quantity': quantities[i],
                    'Price': prices[i],
                    'Title': book_detail['Title'] if book_detail else 'Unknown',
                    'Image': book_detail['image'] if book_detail else 'Unknown',
                    'Genre_id': str(book_detail['Genre']) if book_detail else 'Unknown',
                    'Genre': genre['Theloai']
                }
                items.append(item)
            shop = db.Users.find_one({"_id": order_detail['ShopId']})
            order_details_list.append({
                'OrderId': str(order_detail['OrderId']),
                'Items': items,
                'Total_price': order_detail['Total_price'],
                'DiscountId': str(order_detail['DiscountId']),
                'Status': order_detail['Status'],
                'ShopId': str(order_detail['ShopId']),
                'shop_name': shop['Shop_name']
            })

        return jsonify({'success': True, 'order_details': order_details_list}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@orderDetailBP.route('/order_detail/<user_id>/<status>', methods=['GET'])
def get_order_detail_by_status(user_id, status):
    try:
        user_id = ObjectId(user_id)

        # Dựa vào trạng thái đơn hàng, xây dựng truy vấn cơ sở dữ liệu
        query = {'UserId': user_id, 'Status': status}

        # Truy vấn cơ sở dữ liệu để lấy danh sách các đơn hàng của người dùng có trạng thái nhất định
        order_details = db.OrderDetails.find(query)

        # Biến đổi kết quả thành một danh sách JSON
        order_details_list = []
        for order_detail in order_details:
            # Tạo danh sách các mặt hàng trong đơn hàng
            items = []
            for i in range(len(order_detail['BookId'])):
                item = {
                    'BookId': str(order_detail['BookId'][i]),
                    'Quantity': order_detail['Quantity'][i],
                    'Price': order_detail['Price'][i]
                }
                items.append(item)

            order_details_list.append({
                'OrderId': str(order_detail['_id']),
                'Items': items,
                'Total_price': order_detail['Total_price'],
                'DiscountId': str(order_detail['DiscountId']),
                'ShopId': str(order_detail['ShopId'])
            })

        return jsonify({'success': True, 'order_details': order_details_list}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@orderDetailBP.route('/order_confirm/<order_detail_id>', methods=['PUT'])
def confirm_order(order_detail_id):
    try:
        order_detail_id = ObjectId(order_detail_id)

        # Cập nhật trạng thái của chi tiết đơn hàng thành "shipping"
        db.OrderDetails.update_one({'_id': order_detail_id}, {'$set': {'Status': 'shipping'}})

        return jsonify({'success': True}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500