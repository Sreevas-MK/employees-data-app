from flask import Flask, render_template, session
import mysql.connector
import os
import sys
import json
import redis
from flask_session import Session

def init_database():
    try:
        db = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            passwd=os.getenv('DATABASE_PASSWORD'),
            port=int(os.getenv('DATABASE_PORT', 3306))
        )
        cursor = db.cursor()

        # Create DB if missing
        cursor.execute("CREATE DATABASE IF NOT EXISTS company")
        cursor.execute("USE company")

        # Create table if missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                email VARCHAR(100)
            )
        """)

        db.commit()
        db.close()

    except mysql.connector.Error as e:
        print(f"DB Init Error: {e}", file=sys.stderr)


app = Flask(__name__)

# ---------------------------
# Redis Client (for caching)
# ---------------------------
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=False
)

# ---------------------------
# Flask Session Config (Sticky sessions)
# ---------------------------
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

Session(app)  # initialize Flask-Session

@app.route('/status')
def health_check():
    return 'ok',200

@app.route('/')
def message():
    try:
        # Example: increment page visits for this session
        session['visits'] = session.get('visits', 0) + 1

        # ---------------------------
        # 1. CHECK CACHE FIRST
        # ---------------------------
        cached_data = redis_client.get("employees_cache")
        if cached_data:
            records = json.loads(cached_data)
            return render_template(
                'index.html.tmpl',
                students=records,
                hostname=os.getenv('HOSTNAME', 'Unknown Host'),
                version=os.getenv('APP_VERSION', '1.0'),
                visits=session['visits']
            )

        # ---------------------------
        # 2. QUERY DATABASE IF CACHE EMPTY
        # ---------------------------
        dataBase = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            passwd=os.getenv('DATABASE_PASSWORD'),
            database=os.getenv('DATABASE_NAME', 'company'),
            port=int(os.getenv('DATABASE_PORT', 3306))
        )
        
        cursorObject = dataBase.cursor(dictionary=True)
        table_name = os.getenv('DATABASE_TABLE', 'employees')
        query = f"SELECT * FROM {table_name}"
        cursorObject.execute(query)
        records = cursorObject.fetchall()
        dataBase.close()

        # ---------------------------
        # 3. SAVE TO CACHE
        # ---------------------------
        redis_client.setex("employees_cache", 30, json.dumps(records))

        return render_template(
            'index.html.tmpl',
            students=records,
            hostname=os.getenv('HOSTNAME', 'Unknown Host'),
            version=os.getenv('APP_VERSION', '1.0'),
            visits=session['visits']
        )

    except mysql.connector.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        return "<h3>Database Connection Error</h3><p>Please try again later.</p>", 500

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return "<h3>Application Error</h3><p>An unexpected error occurred.</p>", 500


if __name__ == '__main__':

    required_vars = ['DATABASE_HOST', 'DATABASE_USER', 'DATABASE_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
        sys.exit(1)

    print("Initializing database...")
    init_database()

    hostname = os.getenv('HOSTNAME', None)
    database_host = os.getenv('DATABASE_HOST', None)
    database_port = int(os.getenv('DATABASE_PORT', 3306))
    database_user = os.getenv('DATABASE_USER', None)
    database_password = os.getenv('DATABASE_PASSWORD', None)
    database_name = os.getenv('DATABASE_NAME', 'company')
    database_table = os.getenv('DATABASE_TABLE', 'employees')
    flask_port = int(os.getenv('FLASK_PORT', 3000))
    debug_mode = os.getenv('FLASK_DEBUG', 'True')

    app.run(debug=debug_mode, port=flask_port, host="0.0.0.0")

