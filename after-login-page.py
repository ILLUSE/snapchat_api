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


@app.route('/user-info', methods=['POST'])
def get_user_info_and_friends():
    try:
        # 클라이언트 요청에서 user_id 가져오기
        request_data = request.get_json()
        user_id = request_data.get("user_id")
        cnt_limit = request_data.get("cnt_limit", 3)  # 추천 친구 수 제한

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

        # 추천 친구 정보 쿼리 1: 나를 친구 추가한 사람
        recommend_to_me_query = """
        SELECT DISTINCT u.name AS name, IFNULL(pp.url, "images_0.png") AS url
        FROM T_friend f
        JOIN T_user u ON f.user_id = u.user_id
        LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
        LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
        WHERE f.friend_id = %s
        AND f.user_id NOT IN (
            SELECT friend_id
            FROM T_friend
            WHERE user_id = %s
        )
        ORDER BY u.name;
        """

        # 추천 친구 정보 쿼리 2: 인기 친구 추천
        recommend_popular_query = """
        SELECT DISTINCT u.name AS name, IFNULL(pp.url, "images_0.png") AS url, a.cnt
        FROM (
            SELECT friend_id, COUNT(*) cnt
            FROM T_friend
            WHERE user_id IN (
                SELECT friend_id
                FROM T_friend
                WHERE user_id = %s
            )
            GROUP BY friend_id
        ) a
        JOIN T_user u ON a.friend_id = u.user_id
        LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
        LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
        WHERE a.friend_id NOT IN (
            SELECT friend_id
            FROM T_friend
            WHERE user_id = %s
        )
        AND a.cnt >= %s
        AND a.friend_id != %s
        ORDER BY cnt DESC;
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

        # 추천 친구: 나를 친구로 추가한 사람
        recommend_to_me_df = pd.read_sql_query(recommend_to_me_query, conn, params=[user_id, user_id])
        recommend_to_me = recommend_to_me_df.to_dict(orient="records") if not recommend_to_me_df.empty else []

        # 추천 친구: 인기 친구
        recommend_popular_df = pd.read_sql_query(recommend_popular_query, conn, params=[user_id, user_id, cnt_limit, user_id])
        recommend_popular = recommend_popular_df.to_dict(orient="records") if not recommend_popular_df.empty else []

        # JSON 응답 생성
        return jsonify({
            "userName": user_name,
            "userProfilePicture": user_profile_picture or "default-profile.png",  # 기본 프로필 이미지 설정
            "friends": friends_data,
            "recommendations": {
                "to_me": recommend_to_me,
                "popular": recommend_popular
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
