import json
import os
from pymongo import MongoClient


client = MongoClient("mongodb+srv://Cadejo:0aGnluXd4Y56CviJ@homework08.lgshiv5.mongodb.net/?retryWrites=true&w=majority")
db = client["HomeWork09"]


def load_authors():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    authors_file = os.path.join(current_dir, 'authors.json')
    with open(authors_file, 'r', encoding='utf-8') as file:
        authors_data = json.load(file)
        author_collection = db["authors"]
        author_collection.insert_many(authors_data)


def load_quotes():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    quotes_file = os.path.join(current_dir, 'quotes.json')
    with open(quotes_file, 'r', encoding='utf-8') as file:
        quotes_data = json.load(file)
        quote_collection = db["quotes"]
        quote_collection.insert_many(quotes_data)


if __name__ == '__main__':
    load_authors()
    load_quotes()