from flask import Flask, request, jsonify
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from os import environ
from flask_vite import Vite

load_dotenv()

app = Flask(__name__,static_folder="dist/static",template_folder="dist")

app.config['VITE_DEV_MODE'] = app.config.get('DEBUG')
Vite(app)

key = Fernet.generate_key()


dbname = environ.get('DB_NAME')
user = environ.get('DB_USER')
password = environ.get('DB_PASSWORD')
port = environ.get('DB_PORT')
host = environ.get('DB_HOST')


# CONNECTION TO DATABASE
def get_connection():
    conn = connect(host=host, port=port, user=user, password=password, dbname=dbname)
    return conn


# METHODS CRUD API REST


@app.get("/api/users")
def get_users():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    cur.close()
    conn.close()
    print( jsonify(users))
    return jsonify(users)


@app.post("/api/users")
def add_user():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    new_user = request.get_json()
    username = new_user["username"]
    email = new_user["email"]
    password = Fernet(key).encrypt(bytes(new_user["password"], "utf-8"))

    # %s=> PARAMETERS INTO SQL EXCUTE
    # RETURNING *=>retornar lo insertado
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES(%s,%s,%s) RETURNING *",
        (username, email, password),
    )
    new_user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return jsonify(new_user)


@app.delete("/api/users/<id>")
def delete_user(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    cur.execute('DELETE FROM users WHERE id=%s RETURNING *', (id))
    user_delete = cur.fetchone()
    print(user_delete)
    conn.commit()

    conn.close()
    cur.close()

    return f"User deleted"


@app.put("/api/users/<id>")
def update_user(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    new_user = request.get_json()
    username = new_user['username']
    email = new_user['email']
    password = Fernet(key).encrypt(bytes(new_user['password'],'utf-8')) 

    cur.execute('UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s RETURNING * ',(username,email,password,id))
    
    update_user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    if update_user is None:
        return jsonify({'message':'User not found'}),404

    return jsonify(update_user)


@app.get("/api/users/<id>")
def get_user(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    cur.execute('SELECT * FROM users WHERE id=%s',(id,))
    user = cur.fetchone()

    if user is None:
        return jsonify({'message':'User Not Found'}),404

    return jsonify(user)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True,)
