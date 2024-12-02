'''
Author: Jingwei Wu
Date: 2024-11-27 16:19:54
LastEditTime: 2024-11-27 18:31:07
description: 
'''

from db.mongo import db
from bson import ObjectId
from fastapi import HTTPException, status


async def add_to_cart(user_id: str, product_id: str, quantity: int):
    """
    添加商品到购物车
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than 0"
        )

    # 检查购物车中是否已经存在该商品
    existing_item = await db["carts"].find_one({"user_id": user_id, "product_id": product_id})
    if existing_item:
        # 更新数量
        await db["carts"].update_one(
            {"_id": existing_item["_id"]},
            {"$inc": {"quantity": quantity}}
        )
    else:
        # 新增购物车商品
        new_cart_item = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        }
        await db["carts"].insert_one(new_cart_item)

    return {"message": "Item added to cart successfully"}


async def get_cart(user_id: str):
    """
    获取购物车内容
    """
    cart_items = await db["carts"].find({"user_id": user_id}).to_list(100)

    # 查询商品详情
    product_ids = [item["product_id"] for item in cart_items]
    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(len(product_ids))

    product_map = {str(product["_id"]): product for product in products}
    cart_response = []

    for item in cart_items:
        product = product_map.get(item["product_id"])
        if product:
            cart_response.append({
                "product_id": item["product_id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "total_price": product["price"] * item["quantity"]
            })

    return {"cart": cart_response}


async def update_cart(user_id: str, product_id: str, quantity: int):
    """
    更新购物车商品数量
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than 0"
        )

    result = await db["carts"].update_one(
        {"user_id": user_id, "product_id": product_id},
        {"$set": {"quantity": quantity}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"message": "Cart updated successfully"}


async def remove_from_cart(user_id: str, product_id: str):
    """
    删除购物车中的商品
    """
    result = await db["carts"].delete_one({"user_id": user_id, "product_id": product_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"message": "Item removed from cart successfully"}
