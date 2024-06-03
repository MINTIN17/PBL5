from bson import ObjectId
from flask import Blueprint, request, jsonify
from datetime import datetime
from Demo_web.application import utils
from Demo_web.application.db.db import db

orderBP = Blueprint('order', __name__)


@orderBP.route('/order', methods=['POST'])
def place_order():
    try:
        # Lấy thông tin đơn hàng từ request
        order_data = request.json
        # Kiểm tra dữ liệu đơn hàng
        required_fields = ['userid', 'address', 'status', 'shops', 'shipping_id']
        missing_fields = [field for field in required_fields if field not in order_data]
        if missing_fields:
            return jsonify({'success': False, 'error': f'Thiếu các trường: {missing_fields}'}), 400

        # Lấy thông tin người dùng từ token
        token = request.headers.get('Authorization')
        token = utils.extract_token(token)
        user_id = token.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Token không hợp lệ'}), 401
        user_id = ObjectId(user_id)

        # Chuẩn bị danh sách các sản phẩm trong đơn hàng và tính tổng giá
        order_items = []
        shops_list = []
        total_price = 0
        for shop in order_data['shops']:
            total_price_shop = 0
            for item in shop['books']:
                book_id = item.get('_id')
                quantity = item.get('quantity')
                price = item.get('price')
                title = item.get('title')
                shop_id = item.get('shop_id')
                if shop_id not in shops_list:
                    shops_list.append(shop_id)

                if not book_id or not quantity or not price or not title or not shop_id:
                    return jsonify({'success': False,
                                    'error': 'Các sản phẩm phải chứa book_id, quantity, price, title và shop_id'}), 400

                book_id = ObjectId(book_id)
                shop_id = ObjectId(shop_id)
                item_total_price = price * quantity
                total_price_shop += item_total_price

                order_items.append({
                    '_id': book_id,
                    'quantity': quantity,
                    'price': price,
                    'title': title,
                    'shop_id': shop_id,
                    'total_price': item_total_price
                })

                # Lấy thông tin sách từ cơ sở dữ liệu
                book = db.books.find_one({'_id': ObjectId(book_id)})
                if book is None:
                    return jsonify({'success': False, 'error': 'Sách không tồn tại trong kho'}), 404

                current_quantity = book.get('Quantity', 0)

                # Kiểm tra nếu số lượng yêu cầu lớn hơn số lượng hiện có trong kho
                if quantity > current_quantity:
                    return jsonify({'success': False, 'error': 'Số lượng sách trong kho không đủ'}), 400

                db.books.update_one(
                    {'_id': ObjectId(book_id)},
                    {'$inc': {'Quantity': -quantity}}
                )

                # Kiểm tra và xóa sách khỏi giỏ hàng nếu có
                cart_item = db.Carts.find_one({'user_id': user_id, 'book_id': book_id})
                if cart_item:
                    db.Carts.delete_one({'user_id': user_id, 'book_id': book_id})

                # Lấy thông tin mã giảm giá từ cơ sở dữ liệu
            discount_id = shop.get('discount_id')
            if discount_id:
                discount = db.Discounts.find_one({
                    '_id': ObjectId(discount_id),
                    '$or': [
                        {'DiscountAmount': {'$ne': 0}},
                        {'DiscountPercent': {'$ne': 0}}
                    ]
                })
                if discount:
                    discount_amount = discount.get('DiscountAmount', 0)
                    discount_percent = discount.get('DiscountPercent', 0)
                    # Áp dụng giảm giá cho sản phẩm nếu có
                    if discount_amount != 0:
                        item_discount = discount_amount
                    else:
                        item_discount = total_price_shop * discount_percent / 100
                    total_price_shop -= item_discount



            # Tích lũy tổng giá cho đơn hàng
            total_price += total_price_shop
        # Tính toán tổng giá vận chuyển dựa trên shipping_id và số lượng cửa hàng
        shipping_id = order_data['shipping_id']
        shipping_method = db.ShippingMethods.find_one({'_id': ObjectId(shipping_id)})
        if not shipping_method:
            return jsonify({'success': False, 'error': 'Phương thức vận chuyển không tìm thấy'}), 404
        shipping_cost = shipping_method.get('Cost', 0)
        # Nhân phí vận chuyển với số lượng cửa hàng
        shipping_cost *= len(shops_list)
        total_price += shipping_cost


        # Tạo và lưu đơn hàng vào cơ sở dữ liệu
        current_time = datetime.now()
        order = {
            'OrderDate': current_time,
            'OrderAmount': total_price,
            'UserId': user_id,
            'ShippingMethodId': ObjectId(shipping_id),

        }
        result = db.Orders.insert_one(order)
        order_id = result.inserted_id

        # Cập nhật số lượng sản phẩm trong bảng Discount
        for shop in order_data['shops']:
            discount_id = shop.get('discount_id')
            if discount_id:
                db.Discounts.update_one(
                    {'_id': ObjectId(discount_id)},
                    {'$inc': {'Quantity': -1}}
                )

        # Lưu thông tin chi tiết của từng sản phẩm vào bảng OrderDetails
        for shop in order_data['shops']:
            books_in_shop = []  # Danh sách các ID sách được mua từ cửa hàng này
            quantities = []  # Danh sách số lượng từng sách
            prices = []  # Danh sách giá từng sách
            total_price_shop = 0  # Tổng giá của tất cả các sách từ cửa hàng này

            for item in shop['books']:
                shop_id = item.get('shop_id')  # Lấy ID của cửa hàng
                book_id = item.get('_id')
                books_in_shop.append(book_id)  # Thêm ID sách vào danh sách

                quantity = item.get('quantity')
                quantities.append(quantity)

                price = item.get('price')
                prices.append(price)

                total_price_shop += quantity * price
            # Lấy thông tin giảm giá từ cơ sở dữ liệu (nếu có)
            discount_id = shop.get('discount_id')
            if discount_id:
                discount = db.Discounts.find_one({'_id': ObjectId(discount_id)})
                if discount:
                    discount_amount = discount.get('DiscountAmount', 0)
                    discount_percent = discount.get('DiscountPercent', 0)

                    # Áp dụng giảm giá cho tổng giá của cửa hàng
                    if discount_amount != 0:
                        total_price_shop -= discount_amount
                    else:
                        total_price_shop *= (100 - discount_percent) / 100

            # Cộng thêm phí vận chuyển
            shipping_id = order_data['shipping_id']
            shipping_method = db.ShippingMethods.find_one({'_id': ObjectId(shipping_id)})
            if not shipping_method:
                return jsonify({'success': False, 'error': 'Phương thức vận chuyển không tìm thấy'}), 404
            shipping_cost_per_shop = shipping_method.get('Cost', 0)
            total_price_shop += shipping_cost_per_shop

            order_detail = {
                'OrderId': order_id,
                'BookId': books_in_shop,  # Lưu danh sách các ID sách vào trường BookId
                'Quantity': quantities,
                'Price': prices,
                'Total_price': total_price_shop,  # Tổng giá của tất cả các sách từ cửa hàng này
                'DiscountId': discount_id,
                'ShopId': ObjectId(shop_id),  # Xác định shop_id cho từng order_detail
                'UserId': user_id,
                'Status': order_data['status']
            }
            db.OrderDetails.insert_one(order_detail)

        return jsonify({'success': True, 'message': 'Đặt hàng thành công'}), 201


    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
