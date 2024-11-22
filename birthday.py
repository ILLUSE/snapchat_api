from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/birthday', methods=['POST'])
def birthday_query():
    try:
        request_json = request.get_json()
        user_input = request_json.get('user_id')

        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='qwerty1234',
            db='snapchat'
        )

        sql = """
        SELECT u.name AS name, 
               IFNULL(pp.url, "images/0.png") AS url, 
               DATE_FORMAT(u.birthday, '%%m-%%d') AS birthday
        FROM T_friend f
        JOIN T_user u ON f.friend_id = u.user_id
        LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
        LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
        WHERE f.user_id = %s
        AND MONTH(u.birthday) = MONTH(CURDATE());
        """
        df = pd.read_sql_query(sql, conn, params=(user_input,))

        df_dict = {
            "name": df['name'].tolist(),
            "image": df['url'].tolist(),
            "birthday": df['birthday'].tolist()
        }
        return jsonify(df_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run()