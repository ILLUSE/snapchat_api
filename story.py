from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/story', methods=['POST'])
def story_query():
    conn = None
    try:
        print("Request data:", request.data)
        print("Request headers:", request.headers)

        try:
            request_json = request.get_json(force=True) 
        except Exception:
            return jsonify({"error": "Failed to decode JSON object. Ensure the request body contains valid JSON."}), 400

        if not request_json:
            return jsonify({"error": "Invalid or empty JSON payload"}), 400

        try:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='qwerty1234',
                db='snapchat'
            )
        except pymysql.MySQLError as e:
            return jsonify({"error": f"MySQL Connection Error: {str(e)}"}), 500

        sql = """
        SELECT h.name AS name, s.story_id, sp.url AS story_url, sp.update_time AS upload_time
        FROM T_user_friend_heart h
        JOIN T_story s ON h.user_id = s.user_id
        JOIN T_story_picture sp ON s.story_id = sp.story_id
        WHERE sp.update_time >= '2024-11-21 12:00:00' 
        AND sp.update_time < '2024-11-22 12:00:00'
        ORDER BY sp.update_time DESC;
        """
        df = pd.read_sql_query(sql, conn)

        if df.empty:
            return jsonify({"message": "No results found"}), 200

        df_dict = {
            "name": df['name'].tolist(),
            "story_url": df['story_url'].tolist(),
            "upload_time": df['upload_time'].tolist(),
        }
        return jsonify(df_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)