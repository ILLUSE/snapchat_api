from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/snapchat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 성능 최적화를 위해 비활성화
db = SQLAlchemy(app)

# 비밀번호 변경 라우트 정의
@app.route('/update_password', methods=['PUT'])
def update_password():
    # Postman에서 전달된 입력값 가져오기
    data = request.json
    user_email = data.get('user_email')
    old_password = data.get('old_password')  # 기존 비밀번호
    new_password = data.get('new_password')  # 새 비밀번호

    # SQL 쿼리 실행
    query = """
        UPDATE T_user
        SET password = %s
        WHERE user_email = %s
          AND password = %s;
    """
    try:
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute(query, (new_password, user_email, old_password))
        connection.commit()

        # 변경 확인
        if cursor.rowcount > 0:  # 업데이트된 행이 있을 경우
            return jsonify({
                "message": "Password updated successfully!",
                "previous_password": old_password,
                "new_password": new_password
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
