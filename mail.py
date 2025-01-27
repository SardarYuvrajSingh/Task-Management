import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()


message = Mail(
    from_email='yuvrajs.coding@gmail.com',
    to_emails='s.yuvraj21@ifheindia.org',
    subject='Testing Backend Mail api',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(os.getenv('SENDGRIDAPIKEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)