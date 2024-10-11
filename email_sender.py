import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# SMTP server configuration
smtp_server = EMAIL_SMTP_HOST
smtp_port = 587
sender_email = EMAIL_ADDRESS
password = EMAIL_PASSWORD

# List of recipient emails
recipient_emails = [
    "receipient_email1@gmail.com",
    "receipient_email2@gmail.com",
 ]

def generate_token():
    return str(uuid.uuid4())

def store_token(email, token):
    cursor = conn.cursor()
    query = "INSERT INTO user_tokens (user_email, token, used) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, token, False))
    conn.commit()
    cursor.close()
    conn.close()

def send_email(receiver_email, token):
    encoded_email = receiver_email.replace('@', '%40').replace('.', '%2E')

    # Create the email (MIME format)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "HTML Email Example"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Create the HTML content with the embedded email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Html email</title>
        <style type="text/css">
            /* Styles */
        </style>
    </head>
    <body>
        <center class="wrapper">
            <table class="main" width="100%">
                <!-- LOGO -->
                <tr>
                    <td style="padding: 25px 0 20px; text-align: center; background-color: #f4f4f4; border-bottom: 2px solid #ddd;">
                        <h1 style="margin: 0; color: #333; font-family: Arial, sans-serif; font-size: 24px;">
                            Example_Organisation.com
                        </h1>
                    </td>
                </tr>

                <!-- BODY -->
                <tr>
                    <td style="padding: 0; background-color: #fff;">
                        <table width="100%">
                            <tr>
                                <td style="padding: 0 0 20px; text-align: center;">
                                    <a href="#"><img src="https://i.ibb.co/nDtBp3y/reset.jpg" alt="reset" width="600px" style="border: 0; max-width: 100%;"></a>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 0 ; text-align: center;">
                                    <h1 style="font-size: 25px; margin: 0;">Need our services?</h1>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 15px 0 0; text-align: center;">
                                    <h3 style="font-size: 16px; font-weight: 400; margin: 0;">You are in the right place</h3>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 5px 0 15px; text-align: center;">
                                    <p style="font-size: 16px;line-height: 28px;">Click the button below to view our service</p>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 0 0 0px; text-align: center;">
                                    <a href="#"><img src="https://i.ibb.co/yFjYfr9/click.jpg" alt="click" width="200" style="border: 0; max-width: 200px;"></a>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>

                <!-- FOOTER SECTION -->
                <tr>
                    <td style="padding: 0;">
                        <table width="100%">
                            <tr>
                                <td style="padding: 45px 0 0; text-align: center;">
                                    <h1>We Value Your Feedback!</h1>
                                    <p>Please rate your experience with our service:</p>
                                    <div class="rating">
                                        <a href="https://localhost:5500/rate?star=1&token={token}">⭐</a>
                                        <a href="https://https://localhost:5500/rate?star=2&token={token}">⭐</a>
                                        <a href="https://https://localhost:5500/rate?star=3&token={token}">⭐</a>
                                        <a href="https://https://localhost:5500/rate?star=4&token={token}">⭐</a>
                                        <a href="https://https://localhost:5500/rate?star=5&token={token}">⭐</a>
                                    </div>
                                    <p>Thank you for your feedback!</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </center>
    </body>
    </html>
    """

    plain_text_content = "Hello! Please rate your experience: http://localhost:5000/rate"

    # Attach both plain-text and HTML versions
    msg.attach(MIMEText(plain_text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Sending the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print(f"Email sent to {receiver_email} successfully!")

# Send emails to all recipients
for email in recipient_emails:
    token = generate_token()
    store_token(email, token)
    send_email(email, token)