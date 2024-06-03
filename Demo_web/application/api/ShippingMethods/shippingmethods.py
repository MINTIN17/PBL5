import os

from bson import ObjectId

from Demo_web.application import utils
from Demo_web.application.utils import check_password, hash_password
import jwt
from flask import Blueprint, request, jsonify
shipping_methodBP = Blueprint('shipping', __name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
secret_key = os.getenv('SECRET_KEY')

from Demo_web.application.db.db import db

@shipping_methodBP.get("/method")
def AddOrder():
    try:
        shipping_methods = db.ShippingMethods.find()
        shipping_methods = list(shipping_methods)
        for shipping_method in shipping_methods:
            shipping_method['_id'] = str(shipping_method['_id'])
        return shipping_methods
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})