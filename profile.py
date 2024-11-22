from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/snapchat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 성능 최적화를 위해 비활성화
db = SQLAlchemy(app)

# Flask 라우트 정의
@app.route('/profile', methods=['POST'])
def get_profile():
    # Postman에서 전달된 입력값 가져오기
    data = request.json
    user_email = data.get('user_email')
    password = data.get('password')

# 이메일 , 비밀번호를 입력하면 사용자 정보 출력
# 유저 아이디 , 유저 이메일 , 이름 , 생일 , 가장 최근 업뎃한 프로필 사진

    # SQL 쿼리 실행
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
    try:
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute(query, (user_email, password))
        result = cursor.fetchone()

        if result:
            # 결과를 JSON으로 반환
            return jsonify({
                "user_id": result[0],
                "user_email": result[1],
                "name": result[2],
                "birthday": result[3],
                "profile_picture_url": result[4]
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


