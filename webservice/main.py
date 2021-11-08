from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from time import sleep

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
            data = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return Response("Token is invalid", 401)
        return f(current_user=data['public_id'], *args, **kwargs)

    return wrapper


@app.route("/users", methods=['GET'], endpoint='get_all_users')
@token_requiered
def get_all_users(current_user):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        results = conn.execute(
            "SELECT username, public_id, mail, password FROM users")

    users = []
    for user in results:
        users.append({
            'is_current_user': current_user == user['username'],
            'username': user['username'],
            'public_id': user['public_id'],
            'mail': user['mail'],
            # 'password': user['password']
        })

    return Response(response=jsonify(users), status=200, mimetype='application/json')


@app.route("/user", methods=['POST'], endpoint='create_user')
def create_user():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('mail') or not data.get('password'):
        return Response(response="Missing informations in payload", status=400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT 1 FROM users WHERE mail='{data.get('mail')}'").fetchone()

    if result:
        return Response(response="Mail address already used", status=400)

    data['public_id'] = str(uuid.uuid4())
    hashed_password = generate_password_hash(data['password'], method='sha256')

    with engine.begin() as conn:
        conn.execute(
            f"INSERT INTO users(public_id, username, mail, password) VALUES('{data['public_id']}',  '{data['username']}', '{data['mail']}',  '{hashed_password}')")

    return Response(response=jsonify(public_id=data['public_id'],
                                     username=data['username'],
                                     mail=data['mail'],
                                     password=hashed_password), status=201, mimetype='application/json')


@app.route("/user/<public_id>", methods=['GET'], endpoint='get_user')
@token_requiered
def get_user(current_user, public_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT username, public_id, mail, password FROM users WHERE public_id='{public_id}'").fetchone()

    if result:
        user = {
            'username': result[0],
            'public_id': result[1],
            'mail': result[2],
            'password': result[3]
        }
        return Response(response=jsonify(user), status=200, mimetype='application/json')
    else:
        return Response(response='Unable to find user', status=404)


@app.route("/user/<public_id>", methods=['PUT'], endpoint='update_user')
@token_requiered
def update_user(current_user, public_id):
    if not current_user == public_id:
        return Response(message="Permission denied to update this user", status=403)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT 1 FROM users WHERE public_id='{public_id}'").fetchone()

    if result:
        data = request.get_json()
        if data and data.get('username') and data.get('mail') and data.get('password'):
            hashed_password = generate_password_hash(
                data['password'], method='sha256')
            with engine.begin() as conn:
                conn.execute(
                    f"UPDATE users SET username='{data['username']}', mail='{data['mail']}', password='{hashed_password}' WHERE public_id='{public_id}'")

            return Reponse(response=jsonify(username=data['username'],
                                            public_id=public_id,
                                            mail=data['mail'],
                                            password=hashed_password), status=200)
        else:
            return Response(response="Missing informations in payload", status=400)
    else:
        return Response(response="No user to update", status=404)


@app.route("/user/<public_id>", methods=['DELETE'], endpoint='delete_user')
@token_requiered
def delete_user(current_user, public_id):
    if not current_user == public_id:
        return Response(response="Permission denied to delete this user", status=401)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT 1 FROM users WHERE public_id='{public_id}'").fetchone()

    if not result:
        return Response(status=404)

    with engine.begin() as conn:
        conn.execute(f"DELETE FROM users WHERE public_id='{public_id}'")
    return Response(status=200)


@app.route("/login", methods=['POST'], endpoint='login')
def login():
    data = request.get_json()
    if not data.get('mail') or not data.get('password'):
        return Response(status=400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT username, public_id, mail, password FROM users WHERE mail='{data['mail']}'").fetchone()

    if not result:
        return Response(status=404)

    if check_password_hash(result[3], data['password']):
        payload = {
            'public_id': result[1],
            'username': result[0],
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return jsonify(public_id=result[1],
                       token=token
                       )
    else:
        sleep(seconds=5)
        return Response(status=401)


@app.route("/cigarette", methods=['POST'], endpoint='create_cigarette')
@token_requiered
def create_cigarette(current_user):
    data = request.get_json()
    if not data and not data.get('event_time'):
        return Response(status=400)

    try:
        event_time = datetime.datetime.strptime(
            data.get('event_time'), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return Response(status=400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT 1 FROM users WHERE public_id='{current_user}' and event_time='{event_time}").fetchone()
    if result:
        return Response(status=400)

    with engine.begin() as conn:
        conn.execute(
            f"INSERT INTO smoked_cigarettes(public_user_id, event_time) VALUES('{current_user}', '{event_time}')")

    return Response(status=201)


@app.route("/cigarettes", methods=['GET'], endpoint='get_cigarettes')
@token_requiered
def get_cigarettes(current_user):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        results = conn.execute(
            f"SELECT cigarette_id, event_time FROM smoked_cigarettes WHERE public_user_id='{current_user}'")

    cigarettes = []
    for cigarette in results:
        cigarettes.append({
            'id': cigarette["cigarette_id"],
            'event_time': cigarette["event_time"].strftime('%Y-%m-%d %H:%M:%S')
        })
    return Response(response=jsonify(cigarettes), status=200)


@app.route("/cigarette/<cigarette_id>", methods=['DELETE'], endpoint='delete_cigarette')
@token_requiered
def delete_cigarette(current_user, cigarette_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT 1 FROM smoked_cigarettes WHERE cigarette_id='{cigarette_id}' and public_user_id='{current_user}'").fetchone()

    if not result:
        return Response(status=404)

    with engine.begin() as conn:
        conn.execute(
            f"DELETE FROM smoked_cigarettes WHERE cigarette_id='{cigarette_id}' and public_user_id='{current_user}'")
    return Response(status=200)
