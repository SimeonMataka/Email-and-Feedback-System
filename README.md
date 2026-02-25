# Email & Feedback System

An automated customer feedback pipeline that sends HTML emails with embedded star ratings, collects responses, and performs sentiment analysis on email replies — all backed by a PostgreSQL database. Built with Python, Flask, and TextBlob.

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│  email_sender.py │────▸│   Customer       │────▸│    backend.py       │
│  Sends HTML      │     │   Clicks ⭐ in   │     │    Flask captures    │
│  email with      │     │   email          │     │    rating via /rate  │
│  star ratings    │     │   or replies     │     │    stores in DB      │
└─────────────────┘     └─────────────────┘     └─────────────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ sentiment_analysis.py │
                     │ Reads replies via     │
                     │ IMAP, analyzes        │
                     │ sentiment, routes     │
                     │ feedback by polarity  │
                     └──────────────────────┘
```

1. **Send** — `email_sender.py` dispatches branded HTML emails to a list of recipients, each containing a unique token-protected 1–5 star rating widget
2. **Collect** — When a recipient clicks a star, the Flask backend (`backend.py`) validates the one-time token, records the rating + timestamp, and shows a thank-you page
3. **Analyse** — `sentiment_analysis.py` connects via IMAP, retrieves unread reply emails, strips quoted text, runs TextBlob sentiment analysis, categorises feedback as Positive / Negative / Neutral, saves it to the database, and forwards it to the appropriate team inbox

## Features

- **Embedded star ratings** in HTML emails with one-time-use UUID tokens (prevents duplicate submissions)
- **Sentiment analysis** on free-text email replies using TextBlob polarity scoring
- **Automatic routing** — positive feedback forwarded to one inbox, negative to another
- **Reply extraction** — strips quoted text, signatures, and forwarded headers to isolate the actual reply
- **PostgreSQL storage** — ratings, feedback text, sentiment labels, and timestamps all persisted
- **Environment-based config** — all credentials managed via `.env` file

## Tech Stack

| Component         | Technology                                |
|-------------------|-------------------------------------------|
| **Email sending** | Python `smtplib`, SMTP + TLS              |
| **Email reading** | Python `imaplib`, IMAP4_SSL               |
| **Web server**    | Flask (rating callback endpoint)          |
| **Sentiment**     | TextBlob (NLP polarity analysis)          |
| **Database**      | PostgreSQL via `psycopg2`                 |
| **Deployment**    | Gunicorn                                  |

## Project Structure

```
Email-and-Feedback-System/
├── email_sender.py              # Sends HTML emails with star rating links
├── backend.py                   # Flask app — handles /rate callback, validates tokens
├── sentiment_analysis.py        # IMAP reader + TextBlob sentiment + DB storage + routing
├── database_creation_codes.sql  # SQL schema (user_ratings, email_feedback, user_tokens)
├── env.env                      # Environment variable template
├── requirements.txt             # Python dependencies
└── README.md
```

## Database Schema

| Table              | Purpose                                           |
|--------------------|---------------------------------------------------|
| `user_tokens`      | One-time UUID tokens linked to recipient emails   |
| `user_ratings`     | Star ratings (1–5) with email and timestamp       |
| `email_feedback`   | Reply body text + sentiment label (Pos/Neg/Neu)   |

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- An email account with IMAP & SMTP access (e.g. Gmail with App Passwords)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/SimeonMataka/Email-and-Feedback-System.git
cd Email-and-Feedback-System

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database tables
psql -U your_user -d your_db -f database_creation_codes.sql

# 5. Configure environment variables
#    Copy env.env to .env and fill in your credentials
cp env.env .env
```

### Environment Variables

| Variable                  | Description                          |
|---------------------------|--------------------------------------|
| `EMAIL_IMAP_HOST`         | IMAP server (e.g. `imap.gmail.com`)  |
| `EMAIL_SMTP_HOST`         | SMTP server (e.g. `smtp.gmail.com`)  |
| `EMAIL_ADDRESS`           | Sender email address                 |
| `EMAIL_PASSWORD`          | Sender email password / app password |
| `DB_HOST`                 | PostgreSQL host                      |
| `DB_PORT`                 | PostgreSQL port (default `5432`)     |
| `DB_NAME`                 | Database name                        |
| `DB_USER`                 | Database user                        |
| `DB_PASSWORD`             | Database password                    |
| `POSITIVE_FEEDBACK_EMAIL` | Inbox for positive feedback routing  |
| `NEGATIVE_FEEDBACK_EMAIL` | Inbox for negative feedback routing  |

## Usage

### 1. Send feedback emails

```bash
python email_sender.py
```

Edit the `recipient_emails` list in the script to target your audience.

### 2. Start the rating server

```bash
python backend.py
# or with Gunicorn:
gunicorn backend:app
```

Runs on `http://localhost:5000`. When a recipient clicks a star in their email, it hits `/rate?star=N&token=UUID`.

### 3. Run sentiment analysis

```bash
python sentiment_analysis.py
```

Connects to the inbox via IMAP, processes unread replies, analyses sentiment, stores results, and routes feedback to the appropriate team.

## Author

Built by **Simeon Mataka** — Malawi University of Science and Technology.

## License

© 2024 Simeon Mataka. All rights reserved.
