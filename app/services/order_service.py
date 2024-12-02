'''
Author: Jingwei Wu
Date: 2024-11-27 16:22:15
LastEditTime: 2024-11-27 18:39:56
description: Do not edit
'''

from db.mongo import db
from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime


async def create_order(user_id: str, cart_items: list, total_price: float, address: dict):
    """
    创建订单
    """
    if not cart_items or total_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cart items or total price"
        )
    if not address or not all(key in address for key in ["name", "phone", "address"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address information"
        )

    order_data = {
        "user_id": user_id,
        "items": cart_items,  # 包括商品ID、名称、数量、单价等
        "total_price": total_price,
        "address": address,  # 收货地址
        "status": "Pending",  # 默认状态为待支付
        "created_at": datetime.utcnow().isoformat(),  # ISO格式时间
    }

    result = await db["orders"].insert_one(order_data)

    # 清空购物车中已下单的商品
    product_ids = [item["product_id"] for item in cart_items]
    await db["carts"].delete_many({"user_id": user_id, "product_id": {"$in": product_ids}})

    return {"message": "Order created successfully", "order_id": str(result.inserted_id)}


async def get_user_orders(user_id: str):
    """
    获取用户订单列表
    """
    orders = await db["orders"].find({"user_id": user_id}).sort("created_at", -1).to_list(100)

    order_list = [
        {
            "order_id": str(order["_id"]),
            "items": order["items"],
            "total_price": order["total_price"],
            "status": order["status"],
            "created_at": order["created_at"]
        }
        for order in orders
    ]

    return {"orders": order_list}


async def get_order_details(user_id: str, order_id: str):
    """
    获取订单详情
    """
    order = await db["orders"].find_one({"_id": ObjectId(order_id), "user_id": user_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": str(order["_id"]),
        "items": order["items"],
        "total_price": order["total_price"],
        "address": order["address"],
        "status": order["status"],
        "created_at": order["created_at"]
    }


async def update_order_status(user_id: str, order_id: str, status: str):
    """
    更新订单状态
    """
    valid_statuses = ["Pending", "Paid", "Shipped", "Delivered", "Cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status"
        )

    result = await db["orders"].update_one(
        {"_id": ObjectId(order_id), "user_id": user_id},
        {"$set": {"status": status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or not updated")

    return {"message": f"Order status updated to {status}"}
