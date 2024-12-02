'''
Author: Jingwei Wu
Date: 2024-11-27 16:38:58
LastEditTime: 2024-11-29 17:06:22
description: 
'''

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

uri = "mongodb+srv://jingweik8259:3H5OxusC4zBz8OIe@cluster0.is04n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
   
# uri = "mongodb+srv://jingweik8259:3H5OxusC4zBz8OIe@cluster0.gn9be.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# create a new client and connect to the server
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

db = client.get_database("Shop_db")


# send a ping
try:
    client.admin.command('ping')
    print("Connected to MongoDB Atlas!")
except Exception as e:
    print("Conntection error:", e)

    
# list all databases
print(client.list_database_names())

feedbacks_collection = db['feedbacks']
cart_collection = db['carts']
orders_collection = db['orders']
products_collection = db['products']
users_collection = db['users']