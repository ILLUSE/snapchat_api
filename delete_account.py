from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/snapchat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Postman에서 전달된 입력값 가져오기
    data = request.json
    user_email = data.get('user_email')
    password = data.get('password')

    # 사용자 계정 삭제 전 확인 쿼리
    select_query = """
        SELECT user_id, name
        FROM T_user
        WHERE user_email = %s AND password = %s;
    """

    # 사용자 계정 삭제 쿼리
    delete_query = """
        DELETE FROM T_user
        WHERE user_email = %s AND password = %s;
    """

    try:
        # 데이터베이스 연결
        connection = db.engine.raw_connection()
        cursor = connection.cursor()

        # 계정 존재 여부 확인
        cursor.execute(select_query, (user_email, password))
        user = cursor.fetchone()

        if user:
            # 계정 삭제 실행
            cursor.execute(delete_query, (user_email, password))
            connection.commit()

            if cursor.rowcount > 0:
                return jsonify({
                    "message": "Account deleted successfully",
                    "deleted_user": {
                        "user_id": user[0],
                        "name": user[1],
                        "email": user_email
                    }
                }), 200
            else:
                return jsonify({"message": "Failed to delete account"}), 500
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)

