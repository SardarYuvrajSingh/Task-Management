# from fastapi import APIRouter, Depends
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from model.sql import Tasks
# import io
# from src.connection import get_db  # Ensure this is your database session getter

# router = APIRouter()

# def plot_bar_chart(df: pd.DataFrame):
#     """Create a bar chart for tasks completed per day."""
#     df['completion_day'] = df["completed_date"].dt.date
#     task_counts = df.groupby('completion_day').size()
#     plt.figure(figsize=(10, 6))
#     task_counts.plot(kind='bar')
#     plt.title('Tasks Completed per Day')
#     plt.xlabel('Date')
#     plt.ylabel('Number of Tasks')
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Convert the plot to a BytesIO buffer and return it
#     img_stream = io.BytesIO()
#     plt.savefig(img_stream, format="png")
#     img_stream.seek(0)
#     plt.close()
#     return img_stream

# def plot_pie_chart(df: pd.DataFrame):
#     """Create a pie chart for task distribution by priority."""
#     task_priority_counts = df['task_priority'].value_counts()  # Assuming task_priority is a column
#     plt.figure(figsize=(8, 8))
#     task_priority_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, legend=False)
#     plt.title('Task Distribution by Priority')
#     plt.ylabel('')  # Hide y-axis label

#     # Convert the plot to a BytesIO buffer and return it
#     img_stream = io.BytesIO()
#     plt.savefig(img_stream, format="png")
#     img_stream.seek(0)
#     plt.close()
#     return img_stream

# def plot_line_chart(df: pd.DataFrame):
#     """Create a line chart for task completion trends over time."""
#     df['week_number'] = df["completed_date"].dt.strftime('%Y-%U')
#     completion_counts_per_week = df.groupby('week_number').size()
#     plt.figure(figsize=(10, 6))
#     completion_counts_per_week.plot(kind='line', marker='o')
#     plt.title('Task Completion Trends Over Time')
#     plt.xlabel('Week')
#     plt.ylabel('Number of Completed Tasks')
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Convert the plot to a BytesIO buffer and return it
#     img_stream = io.BytesIO()
#     plt.savefig(img_stream, format="png")
#     img_stream.seek(0)
#     plt.close()
#     return img_stream

# def plot_scatter_plot(df: pd.DataFrame):
#     """Create a scatter plot for time to complete tasks vs task priority."""
#     df['completion_time'] = (df["completed_date"] - df["created_date"]).dt.total_seconds() / 3600  # time in hours
#     plt.figure(figsize=(10, 6))
#     sns.scatterplot(x="task_priority", y="completion_time", data=df)
#     plt.title('Time to Complete Tasks vs Task Priority')
#     plt.xlabel('Task Priority')
#     plt.ylabel('Time to Complete (hours)')
#     plt.tight_layout()

#     # Convert the plot to a BytesIO buffer and return it
#     img_stream = io.BytesIO()
#     plt.savefig(img_stream, format="png")
#     img_stream.seek(0)
#     plt.close()
#     return img_stream

# @router.get('/visualisation/bar', response_class=StreamingResponse, response_model=None)
# def generate_bar_chart(db: Session = Depends(get_db)):
#     tasks = db.query(Tasks).all()
#     tasks_data = [task.__dict__ for task in tasks]

#     df = pd.DataFrame(tasks_data)
#     df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
#     df.dropna(subset=["completed_date", "task_priority"], inplace=True)
    
#     img_stream = plot_bar_chart(df)
#     return StreamingResponse(img_stream, media_type="image/png")

# @router.get('/visualisation/pie', response_class=StreamingResponse, response_model=None)
# def generate_pie_chart(db: Session = Depends(get_db)):
#     tasks = db.query(Tasks).all()
#     tasks_data = [task.__dict__ for task in tasks]

#     df = pd.DataFrame(tasks_data)
#     df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
#     df.dropna(subset=["completed_date", "task_priority"], inplace=True)

#     img_stream = plot_pie_chart(df)
#     return StreamingResponse(img_stream, media_type="image/png")

# @router.get('/visualisation/line', response_class=StreamingResponse, response_model=None)
# def generate_line_chart(db: Session = Depends(get_db)):
#     tasks = db.query(Tasks).all()
#     tasks_data = [task.__dict__ for task in tasks]

#     df = pd.DataFrame(tasks_data)
#     df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
#     df.dropna(subset=["completed_date", "task_priority"], inplace=True)

#     img_stream = plot_line_chart(df)
#     return StreamingResponse(img_stream, media_type="image/png")

# @router.get('/visualisation/scatter', response_class=StreamingResponse, response_model=None)
# def generate_scatter_plot(db: Session = Depends(get_db)):
#     tasks = db.query(Tasks).all()
#     tasks_data = [task.__dict__ for task in tasks]

#     df = pd.DataFrame(tasks_data)
#     df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
#     df.dropna(subset=["completed_date", "task_priority"], inplace=True)

#     img_stream = plot_scatter_plot(df)
#     return StreamingResponse(img_stream, media_type="image/png")

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import matplotlib.pyplot as plt
from model.sql import Tasks,User
import io
from src.connection import get_db  # Ensure this is your database session getter
import logging
from src.OAuth import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def plot_tasks_completed_per_day(df):
    try:
        df['completed_date'] = pd.to_datetime(df['completed_date'])
        df['completed_day'] = df['completed_date'].dt.date
        tasks_per_day = df.groupby('completed_day').size()

        fig = plt.figure(figsize=(10, 6))
        tasks_per_day.plot(kind='bar', color='skyblue')
        plt.title('Tasks Completed per Day', fontsize=16)
        plt.xlabel('Day', fontsize=12)
        plt.ylabel('Number of Tasks', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)  # Rewind the buffer
        return img_buffer
    except Exception as e:
        logger.error(f"Error in plot_tasks_completed_per_day: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating bar chart.")

def plot_task_priority_pie(df):
    """Create a pie chart for task distribution by priority."""
    try:
        # Correct column name "priority" from the Tasks table
        task_priority_counts = df['priority'].value_counts()
        fig = plt.figure(figsize=(8, 8))
        task_priority_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, legend=False)
        plt.title('Task Distribution by Priority', fontsize=16)
        plt.ylabel('')
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)  # Rewind the buffer
        return img_buffer
    except Exception as e:
        logger.error(f"Error in plot_task_priority_pie: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating the pie chart.")

def plot_completion_trends(df):
    """Create a line chart for completion trends over time."""
    try:
        df['completed_date'] = pd.to_datetime(df['completed_date'], errors='coerce')
        df['completion_day'] = df['completed_date'].dt.date
        task_counts = df.groupby('completion_day').size()

        fig = plt.figure(figsize=(10, 6))
        task_counts.plot(kind='line', marker='o')
        plt.title('Completion Trends Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Tasks', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)  # Rewind the buffer
        return img_buffer
    except Exception as e:
        logger.error(f"Error in plot_completion_trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating the line chart.")

def plot_time_to_complete_vs_priority(df):
    """Create a scatter plot for time to complete tasks vs task priorities."""
    try:
        # Ensure dates are parsed as datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['completed_date'] = pd.to_datetime(df['completed_date'], errors='coerce')

        # Calculate time taken to complete each task in days
        df['completion_time'] = (df['completed_date'] - df['created_at']).dt.days
        fig = plt.figure(figsize=(10, 6))
        plt.scatter(df['priority'], df['completion_time'], color='green')
        plt.title('Time to Complete Tasks vs Task Priority', fontsize=16)
        plt.xlabel('Task Priority', fontsize=12)
        plt.ylabel('Completion Time (Days)', fontsize=12)
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)  # Rewind the buffer
        return img_buffer
    except Exception as e:
        logger.error(f"Error in plot_time_to_complete_vs_priority: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating the scatter plot.")

@router.get('/visualisation/{chart_type}', response_class=StreamingResponse)
def generate_chart(chart_type: str, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        # Query tasks data from the database
        tasks = db.query(Tasks).all()
        tasks_data = [task.__dict__ for task in tasks]
        df = pd.DataFrame(tasks_data)

        # Preprocess datetime fields and drop any incomplete entries
        df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
        df.dropna(subset=["completed_date", "priority"], inplace=True)

        # Define a dictionary for selecting the correct chart function
        chart_functions = {
            "bar": plot_tasks_completed_per_day,  # Changed to bar chart
            "pie": plot_task_priority_pie,
            "line": plot_completion_trends,
            "scatter": plot_time_to_complete_vs_priority
        }

        # Check if the requested chart type exists
        if chart_type not in chart_functions:
            raise HTTPException(status_code=400, detail="Invalid chart type. Choose from 'bar', 'pie', 'line', or 'scatter'.")

        # Get the selected chart function and generate the plot
        chart_function = chart_functions[chart_type]
        img_buffer = chart_function(df)

        return StreamingResponse(img_buffer, media_type="image/png")

    except Exception as e:
        logger.error(f"Error in generate_chart: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating the chart.")

