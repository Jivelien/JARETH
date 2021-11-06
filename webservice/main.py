from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config.from_object("config.Config")


def token_requiered(f):
    def wrapper(*args, **kwargs):
        token = None
        if request.args.get("token"):
            token = request.args.get("token")
        if not token:
            return Response("Token is invalid", 401)
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return Response("Token is invalid", 401)
        return f(*args, **kwargs)

    return wrapper

@app.route("/users", methods=['GET'],endpoint='get_all_users')
@token_requiered
def get_all_users():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    results = conn.execute("SELECT username, public_id, mail, password FROM users").fetchall()

    users = []
    for user in results:
        users.append({
            'username': user[0],
            'public_id': user[1],
            'mail': user[2],
            'password': user[3]
        })

    conn.close()
    return jsonify(users)


@app.route("/user", methods=['POST'],endpoint='create_user')
@token_requiered
def create_user():
    data = request.get_json()
    if not data['username'] or not data['mail'] or not data['password']: #FIXME 
        return Response(status=400)
        #TODO check unicity of username and mail

    data['public_id'] = str(uuid.uuid4())
    hashed_password = generate_password_hash(data['password'], method='sha256')

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    conn.execute(f"INSERT INTO users(public_id, username, mail, password) VALUES('{data['public_id']}',  '{data['username']}', '{data['mail']}',  '{hashed_password}')")
    conn.close()

    return  jsonify(public_id = data['public_id'],
                    username = data['username'],
                    mail = data['mail'],
                    password = hashed_password)


@app.route("/user/<public_id>", methods=['GET'],endpoint='get_user')
@token_requiered
def get_user(public_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    result = conn.execute(f"SELECT username, public_id, mail, password FROM users WHERE public_id='{public_id}'").fetchone()

    if result:
        user = {
            'username': result[0],
            'public_id': result[1],
            'mail': result[2],
            'password': result[3]
        }
        conn.close()
        return jsonify(user)
    else:
        conn.close()
        return Response(status=404)


@app.route("/user/<public_id>", methods=['PUT'],endpoint='update_user')
@token_requiered
def update_user(public_id):
    data = request.get_json()
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    result = conn.execute(f"SELECT username, public_id, mail, password FROM users WHERE public_id='{public_id}'").fetchone()

    if result:
        if data['username'] and data['mail'] and data['password']: #FIXME
            hashed_password = generate_password_hash(data['password'], method='sha256')
            conn.execute(f"UPDATE users SET username='{data['username']}', mail='{data['mail']}', password='{hashed_password}' WHERE public_id='{public_id}'")
            conn.close()
            return jsonify(username=data['username'],
                           public_id=public_id,
                           mail=data['mail'],
                           password=hashed_password)
        else:
            conn.close()
            return Response(status=400)
    else:
        conn.close()
        return Response(status=404)


@app.route("/user/<public_id>", methods=['DELETE'],endpoint='delete_user')
@token_requiered
def delete_user(public_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    result = conn.execute(f"SELECT 1 FROM users WHERE public_id='{public_id}'").fetchone()

    if result:
        conn.execute(f"DELETE FROM users WHERE public_id='{public_id}'")
        conn.close()
        return Response(status=200)
    else:
        conn.close()
        return Response(status=404)
    
@app.route("/login", methods=['POST'], endpoint='login')
def login():
    data = request.get_json()
    if not data['mail'] or not data['password']:
        return Response(status=400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    conn = engine.connect()
    result = conn.execute(f"SELECT username, public_id, mail, password FROM users WHERE mail='{data['mail']}'").fetchone()

    if result:
        if check_password_hash(result[3], data['password']):
            payload = {
                'public_id': result[1],
                'username': result[0],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'])
            conn.close()
            return jsonify(public_id=result[1],
                           token=token
                           )
        else:
            conn.close()
            return Response(status=401)
    else:
        conn.close()
        return Response(status=404)
