from flask import Flask, request, jsonify
import pymysql
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/hearted-friend_list', methods=['POST'])
def friend_list_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    start_time = request_json.get('start_time') 
    end_time = request_json.get('end_time')

    try:
        # Connect to the database
        conn = pymysql.connect(host='localhost', port=3306, user='root',
                               password='qwerty1234', db='snapchat')

        # Corrected SQL query
        sql = """
        SELECT 
            u.name AS name, 
            IFNULL(pp.url, "images/0.png") AS url, 
            IF(a.story_upload IS NOT NULL, 1, 0) AS has_story,
            a.story_url
        FROM T_friend f
        JOIN T_user u ON f.friend_id = u.user_id
        LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
        LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
        LEFT JOIN (
            SELECT 
                s.user_id, 
                MAX(sp.update_time) AS story_upload, 
                MAX(sp.url) AS story_url
            FROM T_story s
            JOIN T_story_picture sp ON s.story_id = sp.story_id
            WHERE sp.update_time >= %s
              AND sp.update_time < %s
            GROUP BY s.user_id
        ) a ON u.user_id = a.user_id
        JOIN T_user_friend_heart ufh ON f.friend_id = ufh.user_id
        WHERE f.user_id = %s
        ORDER BY a.story_upload DESC;
        """
        
        # Execute the query using pandas
        df = pd.read_sql_query(sql, conn, params=(start_time, end_time, user_input))

        # Convert DataFrame to dictionary for JSON response
        df_dict = {
            "name": df['name'].tolist(), 
            "image": df['url'].tolist(), 
            "has_story": df['has_story'].tolist(),
            "story_url": df['story_url'].tolist()
        }
        return jsonify(df_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()
    
if __name__ == "__main__":
    app.run()