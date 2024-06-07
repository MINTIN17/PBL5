from bson import ObjectId
from flask import Blueprint, jsonify
from Demo_web.application.db.db import db

statisticalBP = Blueprint('statistical', __name__)

@statisticalBP.route('/pending_confirmation/<shop_id>', methods=['GET'])
def count_pending_orders_by_shop(shop_id):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)

        # Truy vấn cơ sở dữ liệu để đếm số lượng đơn hàng chờ xác nhận của cửa hàng
        pending_orders_count = db.OrderDetails.count_documents({'ShopId': shop_id, 'Status': 'pending'})

        return jsonify({'pending_orders_count': pending_orders_count})

    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi đếm đơn hàng chờ xác nhận cho cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500


@statisticalBP.route('/books_count/<shop_id>', methods=['GET'])
def count_books_sold_by_shop(shop_id):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)
        # Truy vấn cơ sở dữ liệu để lấy ra những cuốn sách của cửa hàng
        shop_books = db.books.find({'SellerId': shop_id})
        # Đếm số lượng cuốn sách
        books_count = len(list(shop_books))
        return jsonify({'books_count': books_count})

    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi đếm số lượng sách của cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500


@statisticalBP.route('/orders_count/<shop_id>/<status>', methods=['GET'])
def count_orders_sold_by_shop_of_status(shop_id, status):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)

        # Truy vấn cơ sở dữ liệu để lấy ra những đơn hàng đã được xác nhận của cửa hàng
        confirmed_orders = db.OrderDetails.find({'ShopId': shop_id, 'Status': status})

        # Đếm số lượng đơn hàng đã được xác nhận
        orders_count = len(list(confirmed_orders))

        return jsonify({'orders_count': orders_count})

    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi đếm số lượng đơn hàng của cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500

@statisticalBP.route('/orders_count/<shop_id>', methods=['GET'])
def count_orders_sold_by_shop(shop_id):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)

        # Truy vấn cơ sở dữ liệu để lấy ra những đơn hàng đã được xác nhận của cửa hàng
        confirmed_orders = db.OrderDetails.find({'ShopId': shop_id})

        # Đếm số lượng đơn hàng đã được xác nhận
        orders_count = len(list(confirmed_orders))

        return jsonify({'orders_count': orders_count})
    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi đếm số lượng đơn hàng của cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500

@statisticalBP.route('/sold_books_count/<shop_id>', methods=['GET'])
def count_sold_books_by_shop(shop_id):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)

        # Truy vấn cơ sở dữ liệu để lấy ra những đơn hàng đã được xác nhận của cửa hàng
        confirmed_orders = db.OrderDetails.find({'ShopId': shop_id, 'Status': 'completed'})

        # Tạo một từ điển để lưu trữ số lượng sách đã bán
        sold_books_count = {}

        # Lặp qua từng đơn hàng
        for order in confirmed_orders:
            # Lặp qua từng sách trong đơn hàng
            for book_id, quantity in zip(order['BookId'], order['Quantity']):
                # Cập nhật số lượng sách đã bán cho từng cuốn sách
                if book_id in sold_books_count:
                    sold_books_count[book_id] += quantity
                else:
                    sold_books_count[book_id] = quantity

        return jsonify(sold_books_count)

    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi thống kê số lượng sách đã bán của cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500


@statisticalBP.route('/buyers_count/<shop_id>', methods=['GET'])
def count_buyers_by_shop(shop_id):
    try:
        # Chuyển đổi shop_id sang đối tượng ObjectId
        shop_id = ObjectId(shop_id)

        # Truy vấn cơ sở dữ liệu để lấy ra những đơn hàng đã được xác nhận của cửa hàng
        confirmed_orders = db.OrderDetails.find({'ShopId': shop_id, 'Status': 'completed'})

        # Tạo một danh sách để lưu trữ các người mua duy nhất
        buyers = set()

        # Lặp qua từng đơn hàng
        for order in confirmed_orders:
            # Thêm user_id của người mua vào danh sách người mua duy nhất
            buyers.add(order['UserId'])

        # Đếm số lượng người mua duy nhất
        buyers_count = len(buyers)

        return jsonify({'buyers_count': buyers_count})

    except Exception as e:
        # Xử lý nếu có lỗi xảy ra
        print(f"Lỗi thống kê số lượng người mua của cửa hàng {shop_id}: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi'}), 500

@statisticalBP.get("/sales_quantity/<shop_id>")
def GetSales_quantity(shop_id):
    sales_quantity = 'Sales_quantity'
    pipeline = [
        {
            '$match': {'SellerId': ObjectId(shop_id)}
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': f'${sales_quantity}'}
            }
        }
    ]
    result = list(db.books.aggregate(pipeline))
    return result

@statisticalBP.get("/total_amount_of_day/<day>")
def Get_Total_Amount_Of_Day(shop_id):
    sales_quantity = 'Sales_quantity'
    pipeline = [
        {
            '$match': {'SellerId': ObjectId(shop_id)}
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': f'${sales_quantity}'}
            }
        }
    ]
    result = list(db.books.aggregate(pipeline))
    return result