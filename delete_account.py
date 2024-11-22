from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    try:
        request_json = request.get_json()
        user_email = request_json.get('user_email')
        password = request_json.get('password')

        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='qwerty1234',
            db='snapchat'
        )
        cursor = conn.cursor()

        select_query = """
            SELECT user_id, name
            FROM T_user
            WHERE user_email = %s AND password = %s;
        """
        delete_query = """
            DELETE FROM T_user
            WHERE user_email = %s AND password = %s;
        """

        cursor.execute(select_query, (user_email, password))
        user = cursor.fetchone()

        if user:
            cursor.execute(delete_query, (user_email, password))
            conn.commit()

            if cursor.rowcount > 0:
                return jsonify({
                    "message": "Account deleted successfully",
                    "deleted_user": {
                        "user_id": user[0],
                        "name": user[1],
                        "email": user_email
                    }
                }), 200
            else:
                return jsonify({"message": "Failed to delete account"}), 500
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)