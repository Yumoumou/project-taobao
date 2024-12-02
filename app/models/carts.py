'''
Author: Jingwei Wu
Date: 2024-11-27 16:13:08
LastEditTime: 2024-11-27 19:06:23
description: 
'''

from pydantic import BaseModel, Field
from typing import List, Optional


class CartItemInDB(BaseModel):
    """
    购物车数据库模型，定义存储在数据库中的购物车商品数据结构
    """
    id: Optional[str] = Field(None, alias="_id")  # MongoDB 的 `_id` 字段
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(..., ge=1, description="商品数量")

    class Config:
        allow_population_by_field_name = True  # 允许使用字段名（如 `_id`）填充数据


class CartItemResponse(BaseModel):
    """
    购物车响应模型，返回购物车中的商品详情
    """
    product_id: str = Field(..., description="商品ID")
    name: str = Field(..., description="商品名称")
    price: float = Field(..., description="商品单价")
    quantity: int = Field(..., description="商品数量")
    total_price: float = Field(..., description="商品总价")


class CartResponse(BaseModel):
    """
    购物车列表响应模型，用于返回整个购物车内容
    """
    cart: List[CartItemResponse] = Field(..., description="购物车商品列表")
