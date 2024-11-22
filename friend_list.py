from flask import Flask, request
import pymysql
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/friend_list', methods=['POST'])
def friend_list_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='qwerty1234', db='snapchat')
    sql = """
    SELECT u.name as name, ifnull(pp.url, "images/0.png") url
    FROM T_friend f
    JOIN T_user u on f.friend_id = u.user_id
    LEFT JOIN T_profile_picture_update ppu on u.user_id = ppu.user_id
    LEFT JOIN T_profile_picture pp on ppu.max_pic_id = pp.pic_id
    WHERE f.user_id = %s
    ORDER BY u.name;
    """% user_input
    
    df = pd.read_sql_query(sql, conn)
    df_dict = {"name": df['name'].tolist(), "image": df['url'].tolist()}
    return df_dict
    
if __name__ == "__main__":
    app.run()