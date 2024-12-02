'''
Author: Jingwei Wu
Date: 2024-11-27 16:31:12
LastEditTime: 2024-11-27 18:50:03
description: 
'''

from db.mongo import db
from fastapi import HTTPException, status
from utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime
from bson import ObjectId


async def register_user(username: str, password: str):
    """
    用户注册
    """
    # 检查用户名是否已经存在
    existing_user = await db["users"].find_one({"username": username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # 加密密码
    hashed_password = hash_password(password)

    # 创建用户记录
    new_user = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
    }

    result = await db["users"].insert_one(new_user)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}


async def login_user(username: str, password: str):
    """
    用户登录
    """
    # 查找用户
    user = await db["users"].find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    # 创建JWT Token
    token = create_access_token({"user_id": str(user["_id"])})
    return {"token": token, "user_id": str(user["_id"])}


async def get_user_profile(user_id: str):
    """
    获取用户个人信息
    """
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user_id": str(user["_id"]), "username": user["username"]}


async def get_user_addresses(user_id: str):
    """
    获取用户地址列表
    """
    addresses = await db["addresses"].find({"user_id": user_id}).to_list(100)
    return {
        "addresses": [
            {
                "id": str(address["_id"]),
                "name": address["name"],
                "phone": address["phone"],
                "address": address["address"],
                "is_default": address["is_default"]
            }
            for address in addresses
        ]
    }


async def add_user_address(user_id: str, name: str, phone: str, address: str, is_default: int = 0):
    """
    新增用户地址
    """
    if is_default == 1:
        # 将其他地址设置为非默认
        await db["addresses"].update_many({"user_id": user_id}, {"$set": {"is_default": 0}})

    new_address = {
        "user_id": user_id,
        "name": name,
        "phone": phone,
        "address": address,
        "is_default": is_default,
    }

    result = await db["addresses"].insert_one(new_address)
    return {"message": "Address added successfully", "address_id": str(result.inserted_id)}


async def update_user_address(user_id: str, address_id: str, name: str, phone: str, address: str, is_default: int = 0):
    """
    更新用户地址
    """
    if is_default == 1:
        # 将其他地址设置为非默认
        await db["addresses"].update_many({"user_id": user_id}, {"$set": {"is_default": 0}})

    result = await db["addresses"].update_one(
        {"_id": ObjectId(address_id), "user_id": user_id},
        {"$set": {"name": name, "phone": phone, "address": address, "is_default": is_default}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Address not found or not updated")

    return {"message": "Address updated successfully"}


async def delete_user_address(user_id: str, address_id: str):
    """
    删除用户地址
    """
    result = await db["addresses"].delete_one({"_id": ObjectId(address_id), "user_id": user_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address deleted successfully"}
