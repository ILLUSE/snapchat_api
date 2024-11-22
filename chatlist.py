from flask import Flask, request
from flask_cors import CORS
import pymysql
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/chatlist', methods=['POST'])
def hearted_chatlist_query():
    try:
        request_json = request.get_json()
        user_input = request_json['user_id']
        conn = pymysql.connect(host='localhost', port=3306, user='root',
                               password='qwerty1234', db='snapchat')
        sql = """
        SELECT IFNULL(cr.name, IF(a.cnt > 3, a.names_3_concat, a.names_3)) AS names, 
            a.cnt, ch.chat, 
            DATE_FORMAT(ch.chat_time, '%%m-%%d %%p %%h:%%i') AS chat_time
        FROM (
        SELECT 
            chm.room_id, 
            COUNT(*) AS cnt, 
            GROUP_CONCAT(u.name) AS names_full,
            SUBSTRING_INDEX(GROUP_CONCAT(u.name), ',', 3) AS names_3,
            CONCAT(SUBSTRING_INDEX(GROUP_CONCAT(u.name), ',', 3), ', ...') AS names_3_concat
        FROM T_chat_member chm
        JOIN T_user u ON chm.user_id = u.user_id 
        WHERE u.user_id != %s
        GROUP BY chm.room_id
        ) a
        JOIN (
        SELECT 
            room_id, 
            MAX(chat_id) AS chat_id
        FROM T_chat
        GROUP BY room_id
        ) b ON a.room_id = b.room_id
        JOIN T_chat ch ON b.chat_id = ch.chat_id
        JOIN T_chat_room cr ON ch.room_id = cr.room_id
        ORDER BY ch.chat_id DESC;
        """% (user_input)
        
        df = pd.read_sql_query(sql, conn)
        conn.close()

        df_dict = {
            "room_name": df['names'].tolist(), 
            "count": df['cnt'].tolist(), 
            "chat": df['chat'].tolist(), 
            "chat_time": df['chat_time'].tolist()
        }
        return df_dict
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run()