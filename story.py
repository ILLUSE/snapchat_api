from flask import Flask, request
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/story', methods=['POST'])
def student_query():
    request_json = request.get_json()
    conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='qwerty1234', db='snapchat')
    sql = """
    SELECT h.name AS name, s.story_id, sp.url AS story_url, sp.update_time as upload_time
    FROM T_user_friend_heart h
    JOIN T_story s ON h.user_id = s.user_id
    JOIN T_story_picture sp ON s.story_id = sp.story_id
    WHERE sp.update_time >= '2024-11-21 12:00:00' 
    AND sp.update_time < '2024-11-22 12:00:00'
    ORDER BY sp.update_time DESC;
    """
    df = pd.read_sql_query(sql, conn)

    df_dict = {
    "name": df['name'].tolist(), "story_url": df['story_url'].tolist(), "upload_time": df['upload_time'].tolist()
    }
    return df_dict

if __name__ == "__main__":
    app.run()