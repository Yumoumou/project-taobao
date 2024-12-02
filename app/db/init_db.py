'''
Author: Jingwei Wu
Date: 2024-11-27 16:39:40
LastEditTime: 2024-11-28 19:36:59
description: Database initialization
'''

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

uri = "mongodb+srv://jingweik8259:3H5OxusC4zBz8OIe@cluster0.is04n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
 
client = AsyncIOMotorClient(uri)
# client = AsyncIOMotorClient("mongodb+srv://your-username:your-password@cluster0.mongodb.net/")
db = client.get_database("Shop_db")

async def initialize_database():
    """initialize database"""

    # await db["products"].create_index("name", unique=True)
    # print("Unique index on 'name' created.")
    
    # # 初始商品数据
    # initial_products = [
    #     {"name": "iphone", "description": "Description A", "price": 100, "stock": 10, "image": "", "purchased_count": 0},
    #     {"name": "bottle", "description": "Description B", "price": 150, "stock": 5, "image": "", "purchased_count": 0},
    # ]
    
    # # 插入数据到 products 集合
    # await db["products"].insert_many(initial_products)
    # print("Product data inserted successfully!")

    # collection = db['users']

    # user_data = {
    #     "username": "Jingwei",
    #     "password": "password123",
    #     "addresses": [
    #         {"name": "Jingwei", "phone": "1234567890", "address": "123 Main St", "is_default": 1},
    #         {"name": "Jingwei", "phone": "9876543210", "address": "456 Office Blvd", "is_default": 0}
    #     ]
    # }

    # result = collection.insert_one(user_data)
    # print("User data inserted successfully!")

    # collection = db['carts']

    # cart_data = {
    #     "user_id": "674851fea6435b4aa28a16d3",
    #     "items": [
    #         {"product_id": "00001", "quantity": 99}
    #     ]
    # }

    # # 插入数据到 users 集合
    # result = collection.insert_one(cart_data)
    # print("Cart data inserted successfully!")


    collection = db['feedbacks']

    feedback_data = {
        "user_id": "674851fea6435b4aa28a16d3",
        "type": "comlaint",
        "message": "too expensice",
        "created_at" : "2024-11-27 16:39:40"
    }

    # 插入数据到 users 集合
    result = collection.insert_one(feedback_data)
    print("feedback data inserted successfully!")

async def main():
    await initialize_database()

# 运行异步任务
asyncio.run(main())
