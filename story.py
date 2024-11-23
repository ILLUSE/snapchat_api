from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/story": {"origins": "*"}})

@app.route('/story', methods=['POST'])
def story_query():
    conn = None
    try:
        print("Request data:", request.data)
        print("Request headers:", request.headers)

        try:
            request_json = request.get_json(force=True) 
            start_time = request_json.get('start_time')  # Fixed syntax
            end_time = request_json.get('end_time')  # Fixed syntax

            # Validate the received data
            if not start_time or not end_time:
                return jsonify({"error": "Missing 'start_time' or 'end_time' in the request body"}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to decode JSON object: {str(e)}"}), 400

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
        SELECT u.name AS name, s.story_id, sp.url AS story_url, sp.update_time AS upload_time
        FROM T_story s 
        JOIN T_story_picture sp ON s.story_id = sp.story_id
        JOIN T_user u ON s.user_id = u.user_id
        WHERE sp.update_time >= %s 
        AND sp.update_time < %s
        ORDER BY sp.update_time DESC;
        """
        df = pd.read_sql_query(sql, conn, params=(start_time, end_time))

        if df.empty:
            return jsonify({"message": "No results found"}), 200

        df_dict = {
            "name": df['name'].tolist(),
            "story_url": df['story_url'].tolist(),
            "upload_time": df['upload_time'].tolist(),
        }
        response = jsonify(df_dict)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)