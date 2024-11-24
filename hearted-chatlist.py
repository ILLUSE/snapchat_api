from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    try:
        return pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='qwerty1234',
            db='snapchat',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")

@app.route('/hearted-chatlist', methods=['POST'])
def hearted_chatlist_query():
    try:
        # Get user input from request
        request_json = request.get_json()
        user_input = request_json.get('user_id')

        if not user_input:
            return jsonify({"error": "user_id is required"}), 400

        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query with placeholders to prevent SQL injection
        sql = """
        SELECT DISTINCT
            cms.names AS names,
            cms.cnt AS member_cnt,
            ch.chat,
            ch.chat_id,
            CASE 
                WHEN ch.user_id != %s THEN (
                    SELECT COUNT(*) 
                    FROM T_chat c 
                    WHERE c.room_id = ch.room_id 
                    AND c.chat_id <= b.chat_id
                    AND c.user_id != %s
                )
                ELSE 0
            END AS chat_cnt,
            DATE_FORMAT(ch.chat_time, '%%m-%%d %%p %%h:%%i') AS chat_time,
            rp.room_photos 
        FROM chat_member_summary cms
        JOIN (
            SELECT 
                room_id, 
                MAX(chat_id) AS chat_id
            FROM T_chat
            GROUP BY room_id
        ) b ON cms.room_id = b.room_id
        JOIN T_chat ch ON b.chat_id = ch.chat_id
        JOIN T_chat_member chm ON ch.room_id = chm.room_id
        JOIN T_user_friend_heart ufh ON ufh.user_id = chm.user_id
        LEFT JOIN room_photos rp ON cms.room_id = rp.room_id
        ORDER BY ch.chat_id DESC;
        """

        # Execute query
        cursor.execute(sql, (user_input, user_input))
        results = cursor.fetchall()

        # Convert results to DataFrame for JSON conversion
        df = pd.DataFrame(results)

        # Close connection
        conn.close()

        # Check if query returned results
        if df.empty:
            return jsonify({"message": "No data found"}), 404

        # Convert DataFrame to dictionary
        df_dict = {
            "room_name": df['names'].tolist(),
            "member_cnt": df['member_cnt'].tolist(),
            "chat": df['chat'].tolist(),
            "chat_cnt": df['chat_cnt'].tolist(),
            "chat_time": df['chat_time'].tolist(),
            "room_photos": df['room_photos'].tolist()
        }

        # Return JSON response
        return jsonify(df_dict)

    except Exception as e:
        # Handle errors gracefully
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)