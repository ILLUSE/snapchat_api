from flask import Flask, request
import pymysql
import pandas as pd

app = Flask(__name__)

@app.route('/recommend-friend_list', methods=['POST'])
def student_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='qwerty1234', db='snapchat')
    sql = """
    SELECT u.name, IFNULL(pp.url, "images/0.png") AS url
    FROM T_friend f
    JOIN T_user u ON f.user_id = u.user_id
    LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
    LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
    WHERE f.friend_id = 1
    AND f.user_id NOT IN (
    SELECT friend_id
    FROM T_friend
    WHERE user_id = %s
    )
    ORDER BY u.name;
    """% user_input
    
    df = pd.read_sql_query(sql, conn)
    df_dict = {"name": df['name'].tolist(), "image": df['url'].tolist()}
    return df_dict
    
if __name__ == "__main__":
    app.run()