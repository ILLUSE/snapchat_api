from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/profile', methods=['POST'])
def get_profile():
    conn = None
    cursor = None
    try:
        request_json = request.get_json()
        user_email = request_json.get('user_email')
        password = request_json.get('password')

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
            u.user_id,
            u.user_email,
            u.name,
            u.birthday,
            pp.url AS profile_picture_url
        FROM 
            T_user u
        LEFT JOIN 
            T_profile_picture pp ON u.user_id = pp.user_id
            AND pp.update_time = (
                SELECT MAX(update_time)
                FROM T_profile_picture
                WHERE user_id = u.user_id
            )
        WHERE 
            u.user_email = %s
            AND u.password = %s;
        """
        cursor.execute(query, (user_email, password))
        result = cursor.fetchone()

        if result:
            return jsonify({
                "user_id": result['user_id'],
                "user_email": result['user_email'],
                "name": result['name'],
                "birthday": result['birthday'],
                "profile_picture_url": result['profile_picture_url']
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)