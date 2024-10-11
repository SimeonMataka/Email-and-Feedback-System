from flask import Flask, request, render_template_string
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Database connection configuration postgresql
db_config = {
    'dbname': 'DB_name',
    'user': 'DB_user',
    'password': 'DB_password',
    'host': 'localhost', #Or your publicly available database
    'port': '5432'  # Default port for PostgreSQL
}

def get_db_connection():
    conn = psycopg2.connect(**db_config)
    return conn

# Route to handle rating submissions
@app.route('/rate', methods=['GET'])
def rate():
    # Retrieve the star rating and token from the URL query parameters
    star_rating = request.args.get('star')
    token = request.args.get('token')

    if not star_rating or not token:
        return "Invalid rating or token", 400

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Validate the token
    check_query = "SELECT user_email FROM user_tokens WHERE token = %s AND used = False"
    cursor.execute(check_query, (token,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return render_template_string(f'''
            <html>
            <head>
                <title>Invalid Token</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f0;
                        color: #333;
                        text-align: center;
                        padding: 50px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #F44336;
                    }}
                    p {{
                        font-size: 18px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                        <h1>Already Rated</h1>
                        <p>You have already submitted a rating. Thank you for your feedback!</p>
                    </div>
            </body>
            </html>
        ''')

    user_email = result[0]

    # Mark the token as used
    update_query = "UPDATE user_tokens SET used = TRUE WHERE token = %s"
    cursor.execute(update_query, (token,))

    # Insert the rating and email into the database along with the timestamp
    insert_query = "INSERT INTO user_ratings (user_email, rating, timestamp) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (user_email, star_rating, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

    # Provide a confirmation message to the user
    return render_template_string(f'''
        <html> 
            <head>
                <title>Thank You!</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f0;
                        color: #333;
                        text-align: center;
                        padding: 50px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #4CAF50;
                    }}
                    p {{
                        font-size: 18px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Thank You!</h1>
                    <p>We received your rating of {star_rating} star(s). Thank you for your feedback!</p>
                </div>
            </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)