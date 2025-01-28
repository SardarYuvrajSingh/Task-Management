import sys
from sqlalchemy.orm import Session
from src.connection import get_db
from model.sql import Tasks, get_timestamp
from src.schemas import TaskCreateSchema,TaskUpdateSchema
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI
from typing import List
from src.OAuth import get_current_user
from model.sql import User
router = APIRouter()


@router.post('/create')
def create_task(task: TaskCreateSchema, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    try:
        # Create a new task instance
        new_task = Tasks(
            name=task.name,
            description=task.description,
            status=task.status,
            due_date=task.due_date,
            assigned_to=task.assigned_to,
            priority=task.priority,
            completed_date=task.completed_date,
            created_at=get_timestamp()
        )

        # Add and commit the task
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {
            "status": "ok",
            "message": "Task created successfully",
            "task_id": new_task.task_id
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete('/task/{task_id}')
def delete_task(task_id: int,  current_user: User = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    try:
        task_to_delete = db.query(Tasks).filter(Tasks.task_id == task_id).first()

        if task_to_delete is None:
            return {
                "status": "error",
                "message": f"Task with id {task_id} not found"
            }

        db.delete(task_to_delete)
        db.commit()

        return {
            "status": "ok",
            "message": f"Task with id {task_id} deleted successfully"
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


@router.put('/test/{task_id}')
def update_task(task_id: int, task: TaskUpdateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        task_to_update = db.query(Tasks).filter(Tasks.task_id == task_id).first()

        if not task_to_update:
            return {"status": "error", "message": f"Task with id {task_id} not found"}

        # Update fields only if they are provided (None means they won't be updated)
        if task.name is not None:
            task_to_update.name = task.name
        if task.description is not None:
            task_to_update.description = task.description
        if task.status is not None:
            task_to_update.status = task.status
            if task.status == "completed":
                task_to_update.completed_date = datetime.now()
        if task.due_date is not None:
            task_to_update.due_date = task.due_date
        if task.assigned_to is not None:
            task_to_update.assigned_to = task.assigned_to
        if task.priority is not None:
            task_to_update.priority = task.priority
        if task.completed_date is not None:
            task_to_update.completed_date = task.completed_date

        db.commit()
        db.refresh(task_to_update)

        return {
            "status": "ok",
            "message": "Task updated successfully",
            "task_id": task_to_update.task_id
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


    
@router.get('/all')
def get_all_tasks( current_user: User = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    try:
        tasks = db.query(Tasks).all()

        if not tasks:
            return {
                "status": "error",
                "message": "No tasks found"
            }

        tasks_data = [TaskCreateSchema.from_orm(task).dict() for task in tasks]

        return {
            "status": "ok",
            "message": "Tasks fetched successfully",
            "tasks": tasks_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get('/tasks/{task_id}')
def get_task_by_id(task_id: int, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    try:
        task = db.query(Tasks).filter(Tasks.task_id == task_id).first()

        if task is None:
            return {
                "status": "error",
                "message": f"Task with id {task_id} not found"
            }

        task_data = TaskCreateSchema.from_orm(task)

        return {
            "status": "ok",
            "message": "Task found",
            "task": task_data.dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    


@router.put('/status/{task_id}')
def update_Task_status(task_id: int, task: TaskUpdateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        task_to_update = db.query(Tasks).filter(Tasks.task_id == task_id).first()

        if not task_to_update:
            return {"status": "error", "message": f"Task with id {task_id} not found"}

        # Update fields only if they are provided (None means they won't be updated)
        if task.name is not None:
            task_to_update.name = task.name
        if task.description is not None:
            task_to_update.description = task.description

        # Use the update_status method to handle status and completed_date
        if task.status is not None:
            task_to_update.update_status(task.status)  # Calls the update_status method

        if task.due_date is not None:
            task_to_update.due_date = task.due_date
        if task.assigned_to is not None:
            task_to_update.assigned_to = task.assigned_to
        if task.priority is not None:
            task_to_update.priority = task.priority

        db.commit()
        db.refresh(task_to_update)

        return {
            "status": "ok",
            "message": "Task updated successfully",
            "task_id": task_to_update.task_id
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
    


@router.post('/multicreate/', response_model=None)
def bulk_insert_tasks(tasks_list: List[TaskCreateSchema], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        # Convert Pydantic models to database instances
        tasks_to_insert = [
            Tasks(
                name=task.name,
                description=task.description,
                status=task.status.value if hasattr(task.status, 'value') else task.status,  # Handle enum value
                due_date=task.due_date,
                assigned_to=task.assigned_to,
                priority=task.priority.value if hasattr(task.priority, 'value') else task.priority,  # Handle enum value
                completed_date=task.completed_date,
                created_at=get_timestamp()  # Use helper function for timestamp
            )
            for task in tasks_list
        ]

        # Add the tasks to the database
        db.add_all(tasks_to_insert)
        db.commit()

        return {
            "status": "ok",
            "message": f"{len(tasks_to_insert)} tasks added successfully"
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }

