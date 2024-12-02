'''
Author: Jingwei Wu
Date: 2024-11-27 16:07:38
LastEditTime: 2024-11-29 21:53:08
description: 
'''
import re
from fastapi import APIRouter, HTTPException, Query
from db.mongo import db
from typing import Optional
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


router = APIRouter()


class ProductListResponse(BaseModel):
    product_id: str
    name: str
    price: float
    image: str
    purchased_count: int

class ProductDetailResponse(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    images: List[str]
    purchased_count: int

class ProductSearchResponse(BaseModel):
    product_id: str
    name: str
    price: float
    images: List[str]
    purchased_count: int


class SearchResponse(BaseModel):
    total_count: int
    products: List[ProductSearchResponse]



@router.get("/api/v1/products", response_model=dict)
async def get_product_list():
    """
    Get list of all products with basic information (name, price, image, purchased_count)
    """

    products = await db["products"].find().to_list(100)  # assume there are less than 100 products

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    product_list = [
        {
            "product_id": str(product["_id"]),
            "name": product.get("name", ""),
            "price": product.get("price", 0.0),
            "image": product.get("images", [""])[0],
            "purchased_count": product.get("purchased_count", 0),
        }
        for product in products
    ]

    return {
        "status": "OK",
        "data": {
            "products": product_list
        }
    }

@router.get("/api/v1/products/{product_id}", response_model=dict)
async def get_product_details(product_id: str):
    """
    Get product details by product_id
    """

    product = await db["products"].find_one({"_id": ObjectId(product_id)})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_response = ProductDetailResponse(
        name=product["name"],
        description=product["description"],
        price=product["price"],
        stock=product["stock"],
        images=product["images"],
        purchased_count=product["purchased_count"],
        seller_id = product["seller_id"]
    )

    return {
        "status": "OK",
        "data": product_response.dict()
    }


@router.post("/api/v1/products/search", response_model=SearchResponse)
async def search_products(name: str):
    """
    根据名称模糊搜索商品
    """
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Search term is too long")
    
    # 输入验证：移除特殊字符，防止正则表达式滥用
    sanitized_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    
    # 使用正则表达式进行模糊匹配，忽略大小写
    query = {"name": {"$regex": sanitized_name, "$options": "i"}}

    products = await db["products"].find(query).to_list(100)

    total_count = len(products)

    if total_count == 0:
        return {
            "status": "OK",
            "data": {
                "total_count": total_count,
                "products": []
            }
        }

    product_list = [
        {
            "product_id": str(product["_id"]),  # MongoDB 的 _id 是 ObjectId，需要转换为字符串
            "name": product.get("name", ""),
            "price": product.get("price", 0.0),
            "images": product.get("images", []),
            "purchased_count": product.get("purchased_count", 0)
        }
        for product in products
    ]

    return {
        "status": "OK",
        "data": {
            "total_count": total_count,
            "products": product_list
        }
    }


# 如果需要分页功能
# @router.get("/api/v1/products", response_model=dict)
# async def get_product_list(limit: int = 20, skip: int = 0):
#     """
#     Get paginated list of products with basic information
#     """
#     # 查询商品，分页
#     products = await db["products"].find().skip(skip).limit(limit).to_list(limit)
    
#     # 如果没有商品
#     if not products:
#         raise HTTPException(status_code=404, detail="No products found")
    
#     # 提取商品的简要信息
#     product_list = [
#         {
#             "name": product.get("name", ""),
#             "price": product.get("price", 0.0),
#             "image": product.get("image", ""),
#             "purchased_count": product.get("purchased_count", 0)
#         }
#         for product in products
#     ]

#     return {
#         "status": "OK",
#         "data": {
#             "products": product_list
#         }
#     }
