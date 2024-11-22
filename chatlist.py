from flask import Flask, request
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/chatlist', methods=['POST'])
def student_query():
    request_json = request.get_json()
    user_input = request_json['user_id']
    conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='qwerty1234', db='snapchat')
    sql = """
    SELECT a.room_id, if(cnt>3, names_3_concat, names_3) names, ch.chat,
    date_format(ch.chat_time, '%%m-%%d %%p %%h:%%i') chat_time
    FROM (
        SELECT chm.room_id, count(*) cnt, group_concat(u.name) names_full,
        substring_index(group_concat(u.name), ',', 3) names_3,
        concat(substring_index(group_concat(u.name), ',', 3), ', ...') names_3_concat
        FROM T_chat_member chm
        JOIN T_user u on chm.user_id = u.user_id
        WHERE u.user_id != %s
        GROUP BY chm.room_id
    ) a
    JOIN (
        SELECT room_id, max(chat_id) chat_id
        FROM T_chat
        GROUP BY room_id
    ) b on a.room_id = b.room_id
    JOIN T_chat ch on b.chat_id = ch.chat_id
    ORDER BY ch.chat_id DESC
    """% (user_input)
    df = pd.read_sql_query(sql, conn)

    df_dict = {
    "name": df['names'].tolist(), "chat": df['chat'].tolist(), "chat_time": df['chat_time'].tolist()
    }
    return df_dict

if __name__ == "__main__":
    app.run()