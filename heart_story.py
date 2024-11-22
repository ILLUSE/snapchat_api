from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/snapchat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# API 엔드포인트 정의 (POST 메서드로 변경)
@app.route('/heart_story', methods=['POST'])
def heart_story():
    # POST 요청에서 필터링 데이터 받기
    data = request.json
    start_time = data.get('start_time', '2024-11-21 12:00:00')  # 기본값 설정
    end_time = data.get('end_time', '2024-11-22 12:00:00')      # 기본값 설정

    query = f"""
    SELECT 
        s.user_id AS friend_id,
        s.story_id,
        sp.url AS story_url,
        sp.update_time
    FROM 
        T_user_friend_heart h
    JOIN 
        T_story s ON h.user_id = s.user_id
    JOIN 
        T_story_picture sp ON s.story_id = sp.story_id
    WHERE 
        sp.update_time >= '{start_time}' 
        AND sp.update_time < '{end_time}'
    ORDER BY 
        sp.update_time DESC;
    """
    try:
        # 데이터베이스 연결 및 쿼리 실행
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        # 결과를 JSON 형식으로 변환
        stories = []
        for row in results:
            stories.append({
                "friend_id": row[0],
                "story_id": row[1],
                "story_url": row[2],
                "update_time": row[3].strftime('%Y-%m-%d %H:%M:%S')  # 날짜 포맷
            })

        return jsonify({"stories": stories}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
