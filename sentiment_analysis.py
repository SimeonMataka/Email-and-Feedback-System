import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from textblob import TextBlob
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
EMAIL_IMAP_HOST = os.getenv("EMAIL_IMAP_HOST")
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

POSITIVE_FEEDBACK_EMAIL = os.getenv("POSITIVE_FEEDBACK_EMAIL")
NEGATIVE_FEEDBACK_EMAIL = os.getenv("NEGATIVE_FEEDBACK_EMAIL")

# Establish the database connection
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Create a cursor object
cur = conn.cursor()

def save_email_feedback(sender_email, email_body, sentiment):
    try:
        # Insert data into the email_feedback table
        cur.execute(
            "INSERT INTO email_feedback (sender_email, body, sentiment) VALUES (%s, %s, %s)",
            (sender_email, email_body, sentiment)
        )
        # Commit the transaction
        conn.commit()
        print("Feedback saved successfully")
    except Exception as e:
        print(f"Error saving feedback: {e}")
        conn.rollback()

# Close the connection when done
def close_db_connection():
    cur.close()
    conn.close()

# Function to strip quoted text and retain only the reply content
def extract_reply(email_body):
    reply_patterns = [
        r'On.*wrote:',  # Matches "On [date], [someone] wrote:"
        r'From:.*',  # Matches forwarded emails with "From:"
        r'^>.*',  # Matches lines that start with ">" (quoted lines)
        r'--\s*\n',  # Matches email signature (starts with "-- ")
        r'forwarded message',  # Matches "Forwarded message"
    ]
    combined_pattern = re.compile('|'.join(reply_patterns), re.IGNORECASE | re.MULTILINE)
    reply_content = re.split(combined_pattern, email_body)[0]
    return reply_content.strip()

# Function to attempt decoding with multiple encodings
def decode_payload(payload):
    try:
        return payload.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return payload.decode('ISO-8859-1')  # Fallback to Latin-1
        except UnicodeDecodeError:
            return payload.decode('windows-1252')  # Another fallback for common encoding

# Function to normalize the subject (remove "Re:" or "Fwd:" prefixes)
def normalize_subject(subject):
    # Remove "Re:", "Fwd:" prefixes and any extra spaces
    normalized_subject = re.sub(r"^(Re:|Fwd:)\s*", "", subject, flags=re.IGNORECASE)
    return normalized_subject


# Function to analyze sentiment and categorize as Positive, Negative, or Neutral
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score


# Function to categorize sentiment
def categorize_sentiment(sentiment_score):
    if sentiment_score > 0:
        return 'Positive'
    elif sentiment_score < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Function to process a text file
def process_text(message):
        sentiment_score = analyze_sentiment(message)
        sentiment_category = categorize_sentiment(sentiment_score)
        return sentiment_category

# Example function to extract email and analyze
def process_email(sender_email, email_body, sentiment):
    # Perform sentiment analysis
    label = process_text(body)

    subject = f"Feedback from {sender_email}"
    
    if sentiment == "Negative":
        print(f"Sending negative feedback to {NEGATIVE_FEEDBACK_EMAIL}")
        send_email(subject, email_body, NEGATIVE_FEEDBACK_EMAIL)
    elif sentiment == "Positive":
        print(f"Sending positive feedback to {POSITIVE_FEEDBACK_EMAIL}")
        send_email(subject, email_body, POSITIVE_FEEDBACK_EMAIL)
    
    # Save the feedback into the database
    save_email_feedback(sender_email, email_body, label)

# Function to send email to the specified recipient
def send_email(subject, body, recipient_email):
    sender_email = EMAIL_ADDRESS
    password = EMAIL_PASSWORD

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the mail server and send the email
    with smtplib.SMTP_SSL(EMAIL_SMTP_HOST, 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())


# Connect to the mail server
mail = imaplib.IMAP4_SSL(EMAIL_IMAP_HOST)
mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

# Select the inbox
mail.select("inbox")

# Search for all unseen emails
status, messages = mail.search(None, 'UNSEEN')

# List of email ids
email_ids = messages[0].split()

# Define the subject you're looking for
desired_subject = "HTML Email Example"

for email_id in email_ids:
    # Fetch the email by id
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):            
            # Parse the email content
            msg = email.message_from_bytes(response_part[1])
            
            # Decode email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # If it's a bytes object, decode it to a string
                subject = subject.decode(encoding or "utf-8")

            # Normalize the subject to remove "Re:", "Fwd:", etc.
            normalized_subject = normalize_subject(subject)

            # Initialize body as an empty string to avoid NameError
            body = ""
            
             # Check if the subject matches
            if normalized_subject == desired_subject:
                # Decode email sender
                sender = msg["From"]

                # Email body (if it's not multipart, just extract)
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            body1 = decode_payload(payload)  # Using custom function for decoding
                            body = extract_reply(body1)  # Custom function to clean up replies
                            print("Sender:", sender)
                            print("Body:", body)
                            # Proceed to sentiment analysis with the body content
                else:
                    payload = part.get_payload(decode=True)
                    body1 = decode_payload(payload)  # Using custom function for decoding
                    body = extract_reply(body1)  # Custom function to clean up replies
                    print("Sender:", sender)
                    print("Body:", body)
                
                # Analyze the sentiment of the body
                sentiment = process_text(body)
                
                # Process email (save to DB and redirect based on sentiment)
                process_email(sender, body, sentiment)

close_db_connection()