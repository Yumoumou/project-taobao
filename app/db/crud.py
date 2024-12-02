'''
Author: Jingwei Wu
Date: 2024-11-27 16:39:18
LastEditTime: 2024-11-27 19:07:20
description: Create, Read, Update, Delete
'''

from db.mongo import db

async def create_item(collection_name: str, data: dict):
    result = await db[collection_name].insert_one(data)
    return result.inserted_id

async def get_item(collection_name: str, query: dict):
    result = await db[collection_name].find_one(query)
    return result

async def update_item(collection_name: str, query: dict, update_data: dict):
    result = await db[collection_name].update_one(query, {"$set": update_data})
    return result.modified_count

async def delete_item(collection_name: str, query: dict):
    result = await db[collection_name].delete_one(query)
    return result.deleted_count
