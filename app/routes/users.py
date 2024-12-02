'''
Author: Jingwei Wu
Date: 2024-11-27 16:07:03
LastEditTime: 2024-11-29 23:14:48
description: 
'''
from fastapi import APIRouter, Depends, HTTPException, status
from db.mongo import db
from utils.auth import get_current_user, create_access_token, verify_password, hash_password
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


class UserRegister(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    status: str
    data: dict


@router.post("/api/v1/users/register", response_model=RegisterResponse)
async def register_user(user: UserRegister):
    """
    User register
    """
    existing_user = await db["users"].find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = {
        "username": user.username,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
    }

    result = await db["users"].insert_one(new_user)

    return {
        "status": "OK",
        "data": {"message": "User registered successfully", "user_id": str(result.inserted_id)}
    }


class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    data: dict

@router.post("/api/v1/users/login", response_model=LoginResponse)
async def login_user(user: UserLogin):
    """
    User login
    """
    existing_user = await db["users"].find_one({"username": user.username})
    
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    token = create_access_token({"user_id": str(existing_user["_id"])})

    return {
        "status": "OK",
        "data": {
            "token": token,
            "user_id": str(existing_user["_id"])
        }
    }

class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    icon: str

class UserProfileApiResponse(BaseModel):
    status: str
    data: UserProfileResponse


@router.get("/api/v1/users/profile", response_model=UserProfileApiResponse)
async def get_user_profile(user: dict = Depends(get_current_user)):
    """
    Get user profile
    """
    user_profile = {
        "user_id": user["user_id"],
        "username": user["username"],
        "icon": user.get("icon", "")
    }
    
    return {
        "status": "OK",
        "data": user_profile
    }


class AddressResponse(BaseModel):
    name: str
    phone: str
    address: str
    is_default: int

class UserAddressesResponse(BaseModel):
    status: str
    data: dict
    addresses: list[AddressResponse] 

@router.get("/api/v1/users/addresses", response_model=UserAddressesResponse)
async def get_user_addresses(user: dict = Depends(get_current_user)):
    """
    Get user's addresses
    """
    user_info = await db["users"].find_one({"user_id": user["user_id"]})
    
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    addresses = user_info.get("addresses", [])


    address_list = [
        {
            "name": address.get("name", ""),
            "phone": address.get("phone", ""),
            "address": address.get("address", ""),
            "is_default": address.get("is_default", 0)
        }
        for address in addresses
    ]

    return {
        "status": "OK",
        "data": {"addresses": address_list}
    }


class Address(BaseModel):
    name: str
    phone: str
    address: str
    is_default: int 


class AddAddressResponse(BaseModel):
    status: str
    data: dict


@router.post("/api/v1/users/addresses", response_model=AddAddressResponse)
async def add_user_address(address: Address, user: dict = Depends(get_current_user)):
    """
    新增用户地址
    """
    user_id = user["user_id"]

    # if set as default address, update other addresses to non-default
    if address.is_default == 1:
        await db["users"].update_many(
            {"user_id": user_id},
            {"$set": {"addresses.is_default": 0}}
        )

    new_address = address.dict()
    new_address["user_id"] = user_id
    
    result = await db["users"].update_one(
        {"user_id": user_id},
        {"$push": {"addresses": new_address}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "OK",
        "data": {"message": "Address added successfully"}
    }


# not update yet
# @router.delete("/api/v1/users/addresses/{address_id}")
# async def delete_user_address(address_id: str, user: dict = Depends(get_current_user)):
#     """
#     删除用户地址
#     """
#     result = await db["addresses"].delete_one(
#         {"_id": address_id, "user_id": user["user_id"]}
#     )
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Address not found")

#     return {"message": "Address deleted successfully"}



# not use
# @router.put("/api/v1/users/addresses/{address_id}")
# async def update_user_address(
#     address_id: str, address: Address, user: dict = Depends(get_current_user)
# ):
#     """
#     更新用户地址
#     """
#     # 如果设置为默认地址，则更新其他地址为非默认
#     if address.is_default == 1:
#         await db["addresses"].update_many(
#             {"user_id": user["user_id"]}, {"$set": {"is_default": 0}}
#         )

#     # 更新指定地址
#     result = await db["addresses"].update_one(
#         {"_id": address_id, "user_id": user["user_id"]},
#         {"$set": address.dict()},
#     )
#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Address not found or not updated")

#     return {"message": "Address updated successfully"}


