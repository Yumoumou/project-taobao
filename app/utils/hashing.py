'''
Author: Jingwei Wu
Date: 2024-11-27 16:35:58
LastEditTime: 2024-11-27 18:52:23
description: 
'''

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    对密码进行加密存储
    :param password: 明文密码
    :return: 加密后的密码
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证登录时的密码是否正确
    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库存储的加密密码
    :return: 验证是否通过
    """
    return pwd_context.verify(plain_password, hashed_password)
