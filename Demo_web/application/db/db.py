from flask_pymongo import MongoClient

client = MongoClient('mongodb+srv://hmtintk:mintin171203.@cluster0.kog6sh2.mongodb.net/web_books?retryWrites=true&w=majority&appName=Cluster0')
db = client['web_books']