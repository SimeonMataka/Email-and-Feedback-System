# Email-and-Feedback-System

This system is designed to manage and analyze customer feedback through email communication. It enables organizations to capture user ratings and perform sentiment analysis on feedback provided by customers via email. The system supports sending HTML emails with an embeded star rating system, collects responses, and stores ratings in a database. Additionally, the system processes email bodies and analyzes sentiment to gauge customer satisfaction.

**#Key-Features**

1. Email Feedback Collection
    - Sends HTML emails to customers, including embedded questions such as:
      How do you rate our service? Users rate using the stars
    - Captures customer responses and stores the data for further analysis.
2. Sentiment Analysis
    - Extracts the email body and sender details from responses.
    - Performs sentiment analysis to classify feedback as positive, negative, or neutral, helping gauge customer sentiment toward the service.
    - Uses Natural Language Processing (NLP) models (e.g., PyTorch, TensorFlow) for sentiment classification.
3. Database Integration
    - Utilizes a PostgreSQL database to store user ratings and email feedback.
    - Captures multiple ratings and stores them in a user_ratings table for easy retrieval and analysis.
    - Database schema supports structured data storage for customer feedback.
4. IMAP Email Handling
    - Connects to email servers (e.g., imap.google.com) using IMAP to retrieve customer feedback emails.
    - Automates the extraction of email bodies and metadata (sender details, time, etc.) for further processing.
  
**#Tech Stack**
  1. Backend: Flask, Python
  2. Database: PostgreSQL
  3. Email Handling: IMAP, SMTP
  4. Feedback Analysis: Sentiment analysis using Textblob

**#Workflow**
    1. Use email_sender.py to send the email to desired receipients
    2. Capture the feedback using the backend.py running flask. Usually on localhost:5500
    3. Run the sentiment analysis to capture the sentiments of the responses from the receipients.
