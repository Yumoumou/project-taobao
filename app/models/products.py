'''
Author: Jingwei Wu
Date: 2024-11-27 16:13:08
LastEditTime: 2024-11-29 16:50:29
description: 
'''

from pydantic import BaseModel, Field
from typing import List, Optional


class ProductInDB(BaseModel):
    """
    商品数据库模型，定义存储在数据库中的商品数据结构
    """
    id: Optional[str] = Field(None, alias="_id")  # MongoDB 的 `_id` 字段
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    description: Optional[str] = Field(None, max_length=1000, description="商品描述")
    price: float = Field(..., gt=0, description="商品价格")
    stock: int = Field(..., ge=0, description="商品库存数量")
    category: Optional[str] = Field(None, max_length=50, description="商品分类")
    images: Optional[List[str]] = Field(default=[], description="商品图片列表")
    purchased_count: int = Field(default=0, ge=0, description="已购买次数")

    class Config:
        allow_population_by_field_name = True  # 允许使用字段名（如 `_id`）填充数据


class ProductResponse(BaseModel):
    """
    商品响应模型，用于返回给客户端的商品信息
    """
    id: str = Field(..., alias="_id")
    name: str = Field(..., description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., description="商品价格")
    stock: int = Field(..., description="商品库存数量")
    category: Optional[str] = Field(None, description="商品分类")
    images: Optional[List[str]] = Field(default=[], description="商品图片列表")
    purchased_count: int = Field(default=0, description="已购买次数")

    class Config:
        allow_population_by_field_name = True  # 允许使用字段名（如 `_id`）填充数据


class ProductSearchInput(BaseModel):
    """
    商品搜索输入模型
    """
    name: str = Field(..., min_length=1, description="商品名称关键词")


class ProductListResponse(BaseModel):
    """
    商品列表响应模型，用于返回商品列表和总数
    """
    total_count: int = Field(..., description="符合条件的商品总数")
    products: List[ProductResponse] = Field(..., description="商品列表")

