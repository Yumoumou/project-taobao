'''
Author: Jingwei Wu
Date: 2024-11-27 16:36:07
LastEditTime: 2024-11-27 18:54:28
description: 
'''


from pydantic import BaseModel, Field, EmailStr, ValidationError

class UserRegistrationValidator(BaseModel):
    """
    用于验证用户注册数据的模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="usename, length between 3 and 10")
    password: str = Field(..., min_length=6, max_length=20, description="password, length between 6 and 20")


class AddressValidator(BaseModel):
    """
    用于验证用户地址数据的模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="name")
    phone: str = Field(..., regex=r"^\d{10,15}$", description="phone number, length between 10 and 15")
    address: str = Field(..., min_length=5, max_length=255, description="收货地址")
    is_default: int = Field(0, ge=0, le=1, description="default address flag, 0 for false, 1 for true")
