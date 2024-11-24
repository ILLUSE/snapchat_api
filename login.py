from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})
app.secret_key = "your_secret_key"

# MySQL 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "qwerty1234",
    "db": "snapchat",
}

@app.route('/login', methods=['POST'])
def login():
    try:
        # 요청 데이터 확인
        data = request.json
        if not data:
            return jsonify({"error": "Request body is missing"}), 400

        email = data.get('user_email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # 데이터베이스 연결
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            query = "SELECT * FROM T_user WHERE user_email = %s AND password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']  # 세션에 사용자 ID 저장
            return jsonify({"name": user['name'], "message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # 연결 닫기
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)





