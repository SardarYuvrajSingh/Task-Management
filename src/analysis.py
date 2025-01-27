from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter, Depends
from src.connection import get_db
from sqlalchemy.orm import Session
from model.sql import Tasks
from datetime import timedelta

router=APIRouter()

@router.get('/task_completion')
def analyze_task_completion_time(db: Session = Depends(get_db)) -> dict:
    """
    Calculate the completion time for each task and the average completion time in both hours and days.
    
    Args:
        db (Session): The SQLAlchemy database session.
        
    Returns:
        dict: A dictionary with completion times for each task in hours and days, 
              and the average time taken in hours and days.
    """
    tasks = db.query(Tasks).all()  # Get all tasks from the database
    task_times_in_days = []
    task_times_in_hours = []

    for task in tasks:
        created_date = task.created_at
        completed_date = task.completed_date
        if completed_date and created_date:
            # Calculate the time taken to complete the task
            time_taken = completed_date - created_date
            time_taken_in_hours = time_taken.total_seconds() / 3600  # in hours
            time_taken_in_days = time_taken_in_hours / 24  # in days

            task_times_in_days.append(time_taken_in_days)
            task_times_in_hours.append(time_taken_in_hours)

    # Calculate average time in hours and days
    average_time_in_hours = sum(task_times_in_hours) / len(task_times_in_hours) if task_times_in_hours else 0
    average_time_in_days = average_time_in_hours / 24  # convert avg hours to days

    return {
        "task_completion_times_in_hours": task_times_in_hours,
        "task_completion_times_in_days": task_times_in_days,
        "average_completion_time_in_hours": average_time_in_hours,
        "average_completion_time_in_days": average_time_in_days
    }


@router.get('/task_overdue')
def analyze_task_overdue(db: Session = Depends(get_db)) -> dict:
    """
    Identify overdue tasks and calculate their percentage.
    
    Args:
        db (Session): The SQLAlchemy database session.
        
    Returns:
        dict: A dictionary with overdue tasks and their percentage.
    """
    tasks = db.query(Tasks).all()  # Get all tasks from the database
    overdue_count = 0
    total_tasks = len(tasks)
    overdue_tasks = []

    for task in tasks:
        due_date = task.due_date
        completed_date = task.completed_date
        if due_date and completed_date:
            if completed_date > due_date:
                overdue_count += 1
                overdue_tasks.append(task)

    overdue_percentage = (overdue_count / total_tasks * 100) if total_tasks > 0 else 0

    return {
        "overdue_tasks": [{"task_id": task.task_id, "name": task.name, "due_date": task.due_date} for task in overdue_tasks],
        "overdue_percentage": overdue_percentage
    }


from sqlalchemy.orm import Session
import pandas as pd


# Cleaning data function
@router.get('/duplicates', response_model=None)
def cleaning_data(db: Session = Depends(get_db)) -> dict:
    tasks = db.query(Tasks).all()  # Get all tasks from the database
    tasks_data = [task.__dict__ for task in tasks]  # Convert tasks to list of dicts
    
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(tasks_data)
    
    # Remove duplicates based on 'task_id' and 'assigned_to'
    df = df.drop_duplicates(subset=["task_id", "assigned_to"])

    # Convert 'due_date' and 'completed_date' to datetime format (invalid dates will be turned into NaT)
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")

    # Return success message
    return {"message": "Data cleaned successfully"}





