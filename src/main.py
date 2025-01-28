import uvicorn
from fastapi import Depends, FastAPI,APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.OAuth import get_current_user
from src.connection import initDB, get_db
import src.analysis
import src.main
import src.operations
import src.visualisation
import os
import src.OAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from model.sql import User

load_dotenv()

app = FastAPI()

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Function to notify about due tasks
def notify_due_tasks():
    from sqlalchemy.orm import Session  # Import here to avoid circular imports
    from model.sql import Tasks        # Ensure your `Tasks` model is correctly defined

    db = next(get_db())  # Get a database session
    try:
        # Query tasks that are due (adjust the filter logic as needed)
        due_tasks = db.query(Tasks).filter(Tasks.completed_date == None).all()
        if due_tasks:
            task_details = "<ul>"
            for task in due_tasks:
                task_details += f"<li>{task.name} (Priority: {task.priority})</li>"
            task_details += "</ul>"

            # Send email with SendGrid
            message = Mail(
                from_email="yuvrajs.coding@gmail.com",
                to_emails="s.yuvraj21@ifheindia.org",
                subject="Pending Task Reminder",
                html_content=f"<p>The following tasks are still due:</p>{task_details}",
            )
            sg = SendGridAPIClient(os.getenv("SENDGRIDAPIKEY"))
            response = sg.send(message)
            print(f"Email sent successfully! Status Code: {response.status_code}")
        else:
            print("No pending tasks to notify.")

    except Exception as e:
        print(f"Error in sending notifications: {e}")
    finally:
        db.close()  # Ensure the database connection is closed


# Start the APScheduler on app startup
@app.on_event("startup")
def startup_event():
    initDB()  # Ensure database tables are initialized
    scheduler.start()
    # Add the notification job every 12 hours
    scheduler.add_job(
        notify_due_tasks,
        trigger=IntervalTrigger(hours=12),
        id="notify_due_tasks",
        replace_existing=True
    )
    print("Scheduler initialized and notification job scheduled.")


# Shutdown the scheduler on app shutdown
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


# Include routers for various functionalities
app.include_router(src.operations.router, tags=["CRUD"])
app.include_router(src.analysis.router, tags=["analysis"])
app.include_router(src.visualisation.router, tags=["Visualisation"])
app.include_router(src.OAuth.router,tags=["Oauth"])

@app.get('/trigger')
def TriggerNotification( current_user: User = Depends(get_current_user)):
    notify_due_tasks()
    return {
        "message":"Notification sent successfully"
    }



@app.get("/", response_class=HTMLResponse)
def landing():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shining Star Yuvraj</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #6200ea;
                color: white;
                text-align: center;
                padding: 2rem 0;
            }
            header h1 {
                font-size: 3rem;
                margin: 0;
            }
            main {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            .highlight {
                color: #ff5722;
                font-weight: bold;
            }
            .emoji {
                font-size: 1.5rem;
                margin-left: 0.5rem;
            }
            .profile-card {
                background: #fff;
                border: 1px solid #ddd;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                max-width: 600px;
                padding: 1.5rem;
                text-align: center;
            }
            .profile-card h2 {
                font-size: 2rem;
                margin-bottom: 1rem;
                color: #6200ea;
            }
            .profile-card p {
                font-size: 1.2rem;
                line-height: 1.8;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Shining Star Yuvraj 🌟</h1>
        </header>
        <main>
            <div class="profile-card">
                <h2>About Yuvraj</h2>
                <p>Yuvraj is a proud <span class="highlight">Punjabi</span> who's always full of energy and charisma. <span class="emoji">💃</span></p>
                <p>He has a deep passion for <span class="highlight">cricket</span>, a game that defines the spirit of perseverance and teamwork. <span class="emoji">🏏</span></p>
                <p>You can often catch him cheering "Bale Bale" in true Punjabi style as he conquers the field and life. <span class="emoji">🥳</span></p>
                <p>Yuvraj is not just a name; it's a symbol of brilliance, whether he's coding, playing cricket, or spreading joy around him!</p>
            </div>
        </main>
    </body>
    </html>
    """

# Run the application
if __name__ == "__main__":
    print("Registered routes:", app.routes)
    uvicorn.run(app, host="127.0.0.1",debug=True)


import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")


