'''
Author: Jingwei Wu
Date: 2024-11-27 16:13:08
LastEditTime: 2024-11-27 19:06:42
description: 
'''

from pydantic import BaseModel, Field
from typing import Optional


class FeedbackInDB(BaseModel):
    """
    Feedback database model defining the structure of feedback stored in the database.
    """
    id: Optional[str] = Field(None, alias="_id")  # MongoDB's `_id` field
    user_id: str = Field(..., description="ID of the user who submitted the feedback")
    type: str = Field(..., description="Feedback type, e.g., suggestion, complaint")
    message: str = Field(..., description="Feedback content/message")
    created_at: Optional[str] = Field(None, description="Timestamp when the feedback was submitted")

    class Config:
        allow_population_by_field_name = True  # Allow population using field names (e.g., `_id`)


class FeedbackCreateInput(BaseModel):
    """
    Input model for creating feedback.
    """
    type: str = Field(..., description="Feedback type, e.g., suggestion, complaint")
    message: str = Field(..., description="Feedback content/message")


class FeedbackResponse(BaseModel):
    """
    Feedback response model returned to the client.
    """
    id: str = Field(..., alias="_id")
    type: str = Field(..., description="Feedback type")
    message: str = Field(..., description="Feedback content")
    created_at: Optional[str] = Field(None, description="Timestamp when the feedback was submitted")

    class Config:
        allow_population_by_field_name = True  # Allow population using field names (e.g., `_id`)


class FeedbackListResponse(BaseModel):
    """
    Feedback list response model for returning multiple feedback entries.
    """
    feedbacks: list[FeedbackResponse] = Field(..., description="List of feedback entries")
