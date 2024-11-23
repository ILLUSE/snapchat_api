from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)  # React와의 CORS 문제 해결

# MySQL 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "qwerty1234",  # 사용자의 MySQL 비밀번호
    "db": "snapchat",          # 데이터베이스 이름
}

@app.route('/after-login-page', methods=['POST'])
def get_friends_and_user_info():
    try:
        # 클라이언트 요청에서 user_id 가져오기
        request_data = request.get_json()
        user_id = request_data.get("user_id")
        
        conn = pymysql.connect(**DB_CONFIG)
        
        # 로그인한 사용자 정보 쿼리
        user_query = """
        SELECT name, 
               (SELECT url 
                FROM T_profile_picture 
                WHERE user_id = %s 
                ORDER BY update_time DESC 
                LIMIT 1) AS user_profile_picture
        FROM T_user
        WHERE user_id = %s;
        """
        
        # 친구 목록 정보 쿼리
        friends_query = """
        SELECT distinct
            u.user_id, 
            u.name, 
            DATE_FORMAT(u.birthday, '%%m-%%d') AS birthday,
            CASE 
                WHEN MONTH(u.birthday) = MONTH(CURDATE()) THEN TRUE 
                ELSE FALSE 
            END AS is_birthday,
            pp.url AS profile_picture
        FROM T_friend f
        JOIN T_user u ON f.friend_id = u.user_id
        LEFT JOIN (
            SELECT user_id, url
            FROM T_profile_picture
            WHERE (user_id, update_time) IN (
                SELECT user_id, MAX(update_time)
                FROM T_profile_picture
                GROUP BY user_id
            )
        ) pp ON u.user_id = pp.user_id
        WHERE f.user_id = %s;
        """

        # 사용자 정보 가져오기
        user_df = pd.read_sql_query(user_query, conn, params=[user_id, user_id])
        if user_df.empty:
            return jsonify({"error": "User not found"}), 404
        
        user_name = user_df.iloc[0]["name"]
        user_profile_picture = user_df.iloc[0]["user_profile_picture"]

        # 친구 목록 가져오기
        friends_df = pd.read_sql_query(friends_query, conn, params=[user_id])
        friends_data = friends_df.to_dict(orient="records") if not friends_df.empty else []

        # JSON 응답 생성
        return jsonify({
            "userName": user_name,
            "userProfilePicture": user_profile_picture or "default-profile.png",  # 기본 프로필 이미지 설정
            "friends": friends_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
