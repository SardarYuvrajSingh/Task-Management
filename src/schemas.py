from pydantic import BaseModel, Field
from datetime import datetime
from typing import List,Optional

#to craete task
class TaskCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = 'pending'
    due_date: datetime
    assigned_to: str = Field(..., min_length=1, max_length=100)
    priority: str = 'low'
    completed_date: Optional[datetime] = None

    class Config:
        orm_mode = True

#To bulk insert
class BulkTaskCreateSchema(BaseModel):
    tasks: List[TaskCreateSchema]

    class Config:
        orm_mode = True

#To fetch the data

class TaskUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    completed_date: Optional[datetime] = None

    class Config:
        orm_mode = True
