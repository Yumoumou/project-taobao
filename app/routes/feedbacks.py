'''
Author: Jingwei Wu
Date: 2024-11-27 16:07:55
LastEditTime: 2024-11-29 17:04:39
description: 
'''

from fastapi import APIRouter, Depends, HTTPException, status
from db.mongo import db
from utils.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class Feedback(BaseModel):
    type: str
    message: str


@router.post("/api/v1/feedback")
async def submit_feedback(feedback: Feedback, user: dict = Depends(get_current_user)):
    """
    Submit feedback
    """
    feedback_data = {
        "user_id": user["user_id"],
        "type": feedback.type,
        "message": feedback.message,
        "created_at": datetime.utcnow().isoformat()
    }

    result = await db["feedbacks"].insert_one(feedback_data)

    return {
        "data": {"message": "Feedback submitted successfully"},
        "status": "OK"
    }


# dont use
# @router.get("/api/v1/feedback")
# async def get_user_feedback(user: dict = Depends(get_current_user)):
#     """
#     Get feedback
#     """
#     feedbacks = await db["feedbacks"].find({"user_id": user["user_id"]}).to_list(100)
#     return {"feedbacks": feedbacks}
