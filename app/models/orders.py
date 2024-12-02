'''
Author: Jingwei Wu
Date: 2024-11-27 16:13:08
LastEditTime: 2024-11-27 19:06:22
description: 
'''

from pydantic import BaseModel, Field
from typing import List, Optional


from pydantic import BaseModel, Field
from typing import List, Optional


class OrderItem(BaseModel):
    """
    订单商品模型，定义订单中的每个商品信息
    """
    product_id: str = Field(..., description="商品ID")
    name: str = Field(..., description="商品名称")
    quantity: int = Field(..., ge=1, description="商品数量")
    price: float = Field(..., gt=0, description="商品单价")


class OrderInDB(BaseModel):
    """
    订单数据库模型，定义存储在数据库中的订单数据结构
    """
    id: Optional[str] = Field(None, alias="_id")  # MongoDB 的 `_id` 字段
    user_id: str = Field(..., description="用户ID")
    items: List[OrderItem] = Field(..., description="订单商品列表")
    total_price: float = Field(..., gt=0, description="订单总金额")
    address: dict = Field(..., description="收货地址，包含 name, phone, address")
    status: str = Field(..., description="订单状态（Pending, Paid, Shipped, Delivered, Cancelled）")
    created_at: Optional[str] = Field(None, description="订单创建时间")

    class Config:
        allow_population_by_field_name = True  # 允许使用字段名（如 `_id`）填充数据


class OrderCreateInput(BaseModel):
    """
    订单创建输入模型
    """
    cart_items: List[OrderItem] = Field(..., description="订单商品列表")
    total_price: float = Field(..., gt=0, description="订单总金额")
    address: dict = Field(..., description="收货地址，包含 name, phone, address")


class OrderResponse(BaseModel):
    """
    订单响应模型，用于返回订单信息
    """
    id: str = Field(..., alias="_id")
    items: List[OrderItem] = Field(..., description="订单商品列表")
    total_price: float = Field(..., description="订单总金额")
    address: dict = Field(..., description="收货地址，包含 name, phone, address")
    status: str = Field(..., description="订单状态")
    created_at: Optional[str] = Field(None, description="订单创建时间")

    class Config:
        allow_population_by_field_name = True  # 允许使用字段名（如 `_id`）填充数据


class OrderListResponse(BaseModel):
    """
    订单列表响应模型，用于返回用户的订单列表
    """
    orders: List[OrderResponse] = Field(..., description="订单列表")
