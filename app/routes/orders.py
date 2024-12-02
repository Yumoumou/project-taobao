'''
Author: Jingwei Wu
Date: 2024-11-27 16:07:47
LastEditTime: 2024-11-29 21:01:40
description: 
'''

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from db.mongo import db
from typing import List
from pydantic import BaseModel
from utils.auth import get_current_user

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CreateOrderRequest(BaseModel):
    cart_items: List[CartItem]

class OrderItemResponse(BaseModel):
    name: str
    description: str
    quantity: int
    image: str
    price: float

class OrderResponse(BaseModel):
    items: List[OrderItemResponse]


class OrderItemResponse(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    image_url: str

class AddressResponse(BaseModel):
    name: str
    phone: str
    address: str

class OrderDetailResponse(BaseModel):
    order_id: str
    address: AddressResponse
    items: List[OrderItemResponse]
    created_at: str


router = APIRouter()

@router.post("/api/v1/orders")
async def create_order(order: dict, user: dict = Depends(get_current_user)):
    """创建订单并从购物车中删除已下单商品"""
    
    user_id = user["user_id"]
    cart_items = order.get("cart_items", [])

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart items are required")

    total_price = 0.0
    products = await db["products"].find({"_id": {"$in": [item["product_id"] for item in cart_items]}}).to_list(len(cart_items))

    # map products by id
    product_map = {str(product["_id"]): product for product in products}

    for item in cart_items:
        product = product_map.get(item["product_id"])
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")

        total_price += product["price"] * item["quantity"]

    order_data = {
        "user_id": user_id,
        "items": cart_items,
        "total_price": total_price,
        "status": "Pending",
        "created_at": datetime.utcnow().isoformat()
    }

    result = await db["orders"].insert_one(order_data)

    # delete items from cart in db
    await remove_items_from_cart(user_id, cart_items)

    return {
        "status": "OK",
        "data": {
            "message": "Order created successfully",
            "order_id": str(result.inserted_id),
            "created_at": order_data["created_at"]
        }
    }



async def remove_items_from_cart(user_id: str, cart_items: list):
    """从购物车中删除已下单的商品"""
    for item in cart_items:
        product_id = item["product_id"]
        result = await db["carts"].delete_one({"user_id": user_id, "product_id": product_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Item {product_id} not found in cart")



@router.get("/api/v1/orders", response_model=dict)
async def get_all_orders(user: dict = Depends(get_current_user)):
    """
    Get all orders for the current user
    """
    user_id = user["user_id"]

    orders = await db["orders"].find({"user_id": user_id}).to_list(100)  # 获取最多100个订单，可以根据需求调整

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    order_responses = []
    for order in orders:
        # get product details for each item in the order
        order_items = []
        for item in order.get("items", []):
            product = await db["products"].find_one({"_id": item["product_id"]})
            if product:
                order_items.append(OrderItemResponse(
                    name=product["name"],
                    description=product["description"],
                    quantity=item["quantity"],
                    image=product["image"],
                    price=product["price"]
                ))

        order_responses.append(OrderResponse(items=order_items))

    return {
        "status": "OK",
        "data": {
            "orders": order_responses
        }
    }



@router.get("/api/v1/orders/{order_id}/details", response_model=dict)
async def get_order_details(order_id: str, user: dict = Depends(get_current_user)):
    """
    Get order details by order_id
    """
    order = await db["orders"].find_one({"_id": order_id, "user_id": user["user_id"]})


    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = []
    for item in order.get("items", []):
        product = await db["products"].find_one({"_id": item["product_id"]})
        if product:
            order_items.append(OrderItemResponse(
                name=product["name"],
                description=product["description"],
                price=product["price"],
                quantity=item["quantity"],
                image_url=product["image"]
            ))

    return {
        "status": "OK",
        "data": {
            "order_id": str(order["_id"]),
            "address": AddressResponse(
                name=order["address"]["name"],
                phone=order["address"]["phone"],
                address=order["address"]["address"]
            ),
            "items": order_items,
            "created_at": order["created_at"]
        }
    }