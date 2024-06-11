from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import redis
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://catalogdb:27017/catalog"
mongo = PyMongo(app)
cache = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

@app.route('/books', methods=['GET'])
def list_books():
    books = list(mongo.db.books.find({}, {'_id': 0}))
    return jsonify(books)

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    cached_book = cache.get(book_id)
    if cached_book:
        return cached_book, 200
    
    book = mongo.db.books.find_one({"id": book_id}, {'_id': 0})
    if book:
        cache.set(book_id, json.dumps(book))
        return jsonify(book), 200
    return jsonify({"message": "Book not found"}), 404

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    mongo.db.books.insert_one(data)
    return jsonify({"message": "Book added successfully"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
