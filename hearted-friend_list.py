from flask import Flask, request
import pymysql
import pandas as pd

app = Flask(__name__)

@app.route('/hearted-friend_list', methods=['POST'])
def friend_list_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='qwerty1234',
        db='snapchat'
    )
    
    sql = """
    SELECT DISTINCT u.name AS name, IFNULL(pp.url, "images/0.png") AS url
    FROM T_friend f
    JOIN T_user u ON f.friend_id = u.user_id
    LEFT JOIN T_profile_picture_update ppu ON u.user_id = ppu.user_id
    LEFT JOIN T_profile_picture pp ON ppu.max_pic_id = pp.pic_id
    JOIN T_user_friend_heart ufh ON f.friend_id = ufh.user_id
    WHERE f.user_id = %s
    ORDER BY u.name;
    """
    df = pd.read_sql_query(sql, conn, params=(user_input,))
    
    df_dict = {
        "name": df['name'].tolist(),
        "image": df['url'].tolist()
    }
    
    conn.close()
    
    return df_dict

if __name__ == "__main__":
    app.run()