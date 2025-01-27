
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

# Define the Status enumeration

# Utility function to get the current timestamp
def get_timestamp():
    return datetime.now()

# SQLAlchemy Base import
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime

base = declarative_base()

# Tasks Table Definition
class Tasks(base):
    __tablename__ = 'Tasks'

    task_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String,default='pending')
    due_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    assigned_to = Column(String, nullable=False)
    priority = Column(String, default='low')
    created_at = Column(DateTime, default=get_timestamp(), nullable=False)


    def update_status(self, status:str):
        """Update task status and set completed_date if the status is 'completed'."""
        self.status = status
        if status == "completed":
            self.completed_date = get_timestamp()  # datetime.datetime.now()
 
    def update_due_date(self, new_due_date: datetime):
        """Update the due date of the task."""
        self.due_date = new_due_date
