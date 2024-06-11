from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import requests

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://orderdb:27017/orders"
mongo = PyMongo(app)

USER_SERVICE_URL = 'http://user-service:5001'
CATALOG_SERVICE_URL = 'http://catalog-service:5002'

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    username = data.get('username')
    book_id = data.get('book_id')
    
    user_response = requests.post(f"{USER_SERVICE_URL}/login", json={"username": username, "password": "dummy_password"})
    if user_response.status_code != 200:
        return jsonify({"message": "Invalid user"}), 401
    
    book_response = requests.get(f"{CATALOG_SERVICE_URL}/books/{book_id}")
    if book_response.status_code != 200:
        return jsonify({"message": "Book not available"}), 404
    
    order = {"username": username, "book_id": book_id}
    mongo.db.orders.insert_one(order)
    return jsonify({"message": "Order created successfully"}), 201

@app.route('/orders/<username>', methods=['GET'])
def get_orders(username):
    orders = list(mongo.db.orders.find({"username": username}, {'_id': 0}))
    return jsonify(orders)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
