from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO visits (visited_at) VALUES (NOW())")
    db.commit()
    cursor.execute("SELECT COUNT(*) FROM visits")
    count = cursor.fetchone()[0]
    db.close()
    return f"Total visits: {count}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
