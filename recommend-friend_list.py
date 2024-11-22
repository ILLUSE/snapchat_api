from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/recommend-friend_list', methods=['POST'])
def student_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    cnt_limit_input = request_json['cnt_limit']

    conn = pymysql.connect(host='localhost', port=3306, user='root',
                           password='qwerty1234', db='snapchat')

    sql_to_me = """
    SELECT u.name as name, IFNULL(pp.url, "images/0.png") AS url
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
    df_to_me = pd.read_sql_query(sql_to_me, conn, params=(user_input, user_input))

    sql_popular = """
    SELECT u.name as name, IFNULL(pp.url, "images/0.png") AS url, a.cnt
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
    df_popular = pd.read_sql_query(sql_popular, conn, params=(user_input, user_input, cnt_limit_input, user_input))

    df_dict = {
        "to_me": {"name": df_to_me['name'].tolist(), "image": df_to_me['url'].tolist()},
        "popular": {"name": df_popular['name'].tolist(), "image": df_popular['url'].tolist()}
    }

    return jsonify(df_dict)

if __name__ == "__main__":
    app.run(debug=True)