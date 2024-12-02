'''
Author: Jingwei Wu
Date: 2024-11-27 16:35:52
LastEditTime: 2024-11-29 17:46:51
description: 
'''

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 60

SECRET_KEY = "your_strong_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """encrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """validate"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Generate a JWT Token with expiration and claims.
    
    - `data` is a dictionary that contains the data you want to include in the JWT (e.g., user_id).
    - `expires_delta` can be used to set the token's custom expiration time. If not provided, it defaults to 1 hour.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Prepare JWT payload (claims)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})  # 添加过期时间(exp)和签发时间(iat)
    
    # create Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # 你的Token认证端点

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT and get user info"""
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user ID"
            )
        return {"user_id": user_id}  # 或者返回其他用户信息，视乎你的token结构
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )

# def get_current_user(token: str = Depends()):
#     """validate JWT and get info"""
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")


