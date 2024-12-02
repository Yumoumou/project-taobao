'''
Author: Jingwei Wu
Date: 2024-11-27 16:07:23
LastEditTime: 2024-11-29 21:02:39
description: 
'''

from fastapi import APIRouter, Depends, HTTPException, status
from db.mongo import db
from utils.auth import get_current_user
from pydantic import BaseModel
from bson import ObjectId


router = APIRouter()

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartItemResponse(BaseModel):
    product_id: str
    name: str
    quantity: int
    price: float
    image: str

class RemoveCartItem(BaseModel):
    product_id: str


@router.post("/api/v1/cart")
async def add_to_cart(item: CartItem, user: dict = Depends(get_current_user)):
    """
    Add item to cart
    """
    if item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than 0"
        )

    # 检查商品是否已在购物车中
    cart_item = {
        "user_id": user["user_id"],
        "product_id": item.product_id,
        "quantity": item.quantity,
    }
    await db["carts"].update_one(
        {"user_id": user["user_id"], "product_id": item.product_id},
        {"$inc": {"quantity": item.quantity}},
        upsert=True
    )

    return {"status": "OK", "data": {"message": "Item added to cart successfully"}}


@router.get("/api/v1/cart", response_model=dict)
async def get_cart(user: dict = Depends(get_current_user)):
    """
    Get cart - returns all items in the user's cart with product details
    """
    cart_items = await db["carts"].find({"user_id": user["user_id"]}).to_list(100)
    
    if not cart_items:
        return {"status": "OK", "data": {"cart": []}}

    product_ids = [item["product_id"] for item in cart_items]
    
    products = await db["products"].find({"_id": {"$in": [ObjectId(pid) for pid in product_ids]}}).to_list(len(product_ids))

    # map product_id to product 通过映射 (product_map) 优化查询效率?
    product_map = {str(product["_id"]): product for product in products}

    cart_response = []
    for item in cart_items:
        product = product_map.get(item["product_id"])  # get product info
        if product:
            cart_response.append({
                "product_id": item["product_id"],
                "name": product.get("name", "Unknown"),  # if no product name, use default value
                "quantity": item["quantity"],
                "price": product.get("price", 0.0),
                "image": product.get("image", "")
            })

    return {"status": "OK", "data": {"cart": cart_response}}


@router.delete("/api/v1/cart/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    """
    delete product from cart
    """
    result = await db["carts"].delete_one({"user_id": user["user_id"], "product_id": product_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {
        "status": "OK",
        "data": {"message": "Item removed from cart"}
    }


# @router.put("/api/v1/cart/{product_id}")
# async def update_cart(product_id: str, quantity: int, user: dict = Depends(get_current_user)):
#     """
#     update quantity in cart
#     """
#     if quantity <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than 0"
#         )

#     result = await db["carts"].update_one(
#         {"user_id": user["user_id"], "product_id": product_id},
#         {"$set": {"quantity": quantity}}
#     )

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Cart item not found")

#     return {"message": "Cart updated successfully"}








# @router.get("/api/v1/cart")
# async def get_cart(user: dict = Depends(get_current_user)):
#     """
#     Get cart
#     """
#     cart_items = await db["carts"].find({"user_id": user["user_id"]}).to_list(100)

#     # get product info
#     product_ids = [item["product_id"] for item in cart_items]
#     products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(len(product_ids))

#     product_map = {product["_id"]: product for product in products}
#     cart_response = []

#     for item in cart_items:
#         product = product_map.get(item["product_id"])
#         if product:
#             cart_response.append({
#                 "product_id": product["_id"],
#                 "name": product["name"],
#                 "price": product["price"],
#                 "quantity": item["quantity"],
#                 "total_price": product["price"] * item["quantity"]
#             })

#     return {"cart": cart_response}
