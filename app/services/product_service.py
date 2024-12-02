'''
Author: Jingwei Wu
Date: 2024-11-27 16:31:18
LastEditTime: 2024-11-27 18:49:04
description: 
'''

from db.mongo import db
from fastapi import HTTPException, status


async def get_products(category: str = None, page: int = 1, limit: int = 10):
    """
    获取商品列表，支持分类筛选和分页
    """
    query = {}
    if category:
        query["category"] = category

    # 分页处理
    skip = (page - 1) * limit
    products_cursor = db["products"].find(query).skip(skip).limit(limit)
    products = await products_cursor.to_list(length=limit)

    # 统计符合条件的商品总数
    total_count = await db["products"].count_documents(query)

    # 格式化返回结果
    product_list = [
        {
            "id": str(product["_id"]),
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "stock": product["stock"],
            "category": product["category"],
            "images": product.get("images", []),
            "purchased_count": product.get("purchased_count", 0),
        }
        for product in products
    ]

    return {"total_count": total_count, "products": product_list}


async def get_product_detail(product_id: str):
    """
    获取商品详情
    """
    product = await db["products"].find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "price": product["price"],
        "stock": product["stock"],
        "category": product["category"],
        "images": product.get("images", []),
        "purchased_count": product.get("purchased_count", 0),
    }


async def search_products(name: str):
    """
    搜索商品
    """
    query = {"name": {"$regex": name, "$options": "i"}}  # 模糊搜索，忽略大小写
    products = await db["products"].find(query).to_list(length=100)

    # 格式化返回结果
    product_list = [
        {
            "id": str(product["_id"]),
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "stock": product["stock"],
            "category": product["category"],
            "images": product.get("images", []),
            "purchased_count": product.get("purchased_count", 0),
        }
        for product in products
    ]

    return {"total_count": len(product_list), "products": product_list}


async def increment_purchase_count(product_id: str, count: int = 1):
    """
    增加商品的已购买次数
    """
    if count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Count must be greater than 0"
        )

    result = await db["products"].update_one(
        {"_id": product_id},
        {"$inc": {"purchased_count": count}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Purchase count updated"}
