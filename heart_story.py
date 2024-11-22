from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/heart_story', methods=['POST'])
def heart_story():
    conn = None
    cursor = None
    try:
        request_json = request.get_json()
        start_time = request_json.get('start_time', '2024-11-21 12:00:00')  
        end_time = request_json.get('end_time', '2024-11-22 12:00:00')      

        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='qwerty1234',
            db='snapchat',
            cursorclass=pymysql.cursors.DictCursor  
        )
        cursor = conn.cursor()

        query = """
        SELECT 
            s.user_id AS friend_id,
            s.story_id,
            sp.url AS story_url,
            sp.update_time
        FROM 
            T_user_friend_heart h
        JOIN 
            T_story s ON h.user_id = s.user_id
        JOIN 
            T_story_picture sp ON s.story_id = sp.story_id
        WHERE 
            sp.update_time >= %s 
            AND sp.update_time < %s
        ORDER BY 
            sp.update_time DESC;
        """
        cursor.execute(query, (start_time, end_time))
        results = cursor.fetchall()

        stories = []
        for row in results:
            stories.append({
                "friend_id": row['friend_id'],
                "story_id": row['story_id'],
                "story_url": row['story_url'],
                "update_time": row['update_time'].strftime('%Y-%m-%d %H:%M:%S') 
            })

        return jsonify({"stories": stories}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)