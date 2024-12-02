'''
Author: Jingwei Wu
Date: 2024-11-27 16:31:24
LastEditTime: 2024-11-27 18:42:54
description: 
'''


from db.mongo import db
from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime


async def submit_feedback(user_id: str, feedback_type: str, message: str):
    """
    提交用户反馈
    """
    if not feedback_type or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback type and message are required"
        )

    feedback_data = {
        "user_id": user_id,
        "type": feedback_type,
        "message": message,
        "created_at": datetime.utcnow().isoformat()  # ISO格式时间戳
    }

    result = await db["feedbacks"].insert_one(feedback_data)

    return {"message": "Feedback submitted successfully", "feedback_id": str(result.inserted_id)}


async def get_user_feedback(user_id: str):
    """
    获取用户的所有反馈记录
    """
    feedbacks = await db["feedbacks"].find({"user_id": user_id}).to_list(100)

    # 格式化反馈记录
    feedback_list = [
        {
            "id": str(feedback["_id"]),
            "type": feedback["type"],
            "message": feedback["message"],
            "created_at": feedback["created_at"]
        }
        for feedback in feedbacks
    ]

    return {"feedbacks": feedback_list}


async def get_feedback_by_id(user_id: str, feedback_id: str):
    """
    根据反馈ID获取单条反馈记录
    """
    feedback = await db["feedbacks"].find_one({"_id": ObjectId(feedback_id), "user_id": user_id})
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return {
        "id": str(feedback["_id"]),
        "type": feedback["type"],
        "message": feedback["message"],
        "created_at": feedback["created_at"]
    }
