'''
Author: Jingwei Wu
Date: 2024-11-27 16:13:08
LastEditTime: 2024-11-27 19:02:48
description: 
'''

from pydantic import BaseModel, Field
from typing import Optional

class UserInDB(BaseModel):
    """
    用户数据库模型，定义存储在数据库中的用户数据结构
    """
    id: Optional[str] = Field(None, alias="_id")  # MongoDB 的 `_id` 字段
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., description="加密后的密码")
    created_at: Optional[str] = Field(None, description="用户创建时间")

    class Config:
        allow_population_by_field_name = True  # 允许用字段名（如 `_id`）填充数据


class UserRegister(BaseModel):
    """
    用户注册时的输入数据模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserResponse(BaseModel):
    """
    用户信息的响应数据模型（不包含敏感信息）
    """
    id: str = Field(..., alias="_id")
    username: str = Field(..., description="用户名")

    class Config:
        allow_population_by_field_name = True  # 允许用字段名（如 `_id`）填充数据
