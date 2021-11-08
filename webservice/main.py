from flask import Flask, jsonify, request, Response, make_response
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

    return jsonify(users)


@app.route("/user", methods=['POST'], endpoint='create_user')
def create_user():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('mail') or not data.get('password'):
        return make_response(jsonify(message="Missing informations in payload"), 400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        query_parameters = (data.get('mail'),)
        query = '''
                    SELECT 1 FROM users WHERE mail=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()

    if result:
        return make_response(jsonify(message="Mail address already used"), 400)

    data['public_id'] = str(uuid.uuid4())
    hashed_password = generate_password_hash(data['password'], method='sha256')

    with engine.begin() as conn:
        query_parameters = (data['public_id'], data['username'], data['mail'], hashed_password)
        query = '''
                INSERT INTO users(public_id, username, mail, password) 
                VALUES(%s, %s, %s, %s)
                '''
        conn.execute(query, query_parameters)

    return make_response(jsonify(public_id=data['public_id'],
                                     username=data['username'],
                                     mail=data['mail'],
                                     password=hashed_password), 201)


@app.route("/user/<public_id>", methods=['GET'], endpoint='get_user')
@token_requiered
def get_user(current_user, public_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        query_parameters = (public_id,)
        query = '''
                SELECT username, public_id, mail, password 
                FROM users 
                WHERE public_id=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()

    if result:
        user = {
            'username': result[0],
            'public_id': result[1],
            'mail': result[2],
            'password': result[3]
        }
        return jsonify(user)
    else:
        return make_response(jsonify(message='Unable to find user'), 404)


@app.route("/user/<public_id>", methods=['PUT'], endpoint='update_user')
@token_requiered
def update_user(current_user, public_id):
    if not current_user == public_id:
        return make_response(jsonify(message="Permission denied to update this user"), 403)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        query_parameters = (public_id,)
        query = '''
                SELECT 1 
                FROM users 
                WHERE public_id=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()

    if result:
        data = request.get_json()
        if data and data.get('username') and data.get('mail') and data.get('password'):
            hashed_password = generate_password_hash(data['password'], method='sha256')
            with engine.begin() as conn:
                query_parameters = (data['username'], data['mail'], hashed_password, public_id)
                query = '''
                        UPDATE users 
                        SET username=%s, mail=%s, password=%s
                        WHERE public_id=%s
                        '''
                conn.execute(query, query_parameters)

            return jsonify(username=data['username'],
                           public_id=public_id,
                           mail=data['mail'],
                           password=hashed_password)
        else:
            return make_response(jsonify(message="Missing informations in payload"), 400)
    else:
        return make_response(jsonify(message="No user to update"), 404)


@app.route("/user/<public_id>", methods=['DELETE'], endpoint='delete_user')
@token_requiered
def delete_user(current_user, public_id):
    if not current_user == public_id:
        return make_response(jsonify(message="Permission denied to delete this user"), 401)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        query_parameters = (public_id,)
        query = '''
                SELECT 1
                FROM users
                WHERE public_id=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()

    if not result:
        return make_response(jsonify(message="Unknow user"), 404)

    with engine.begin() as conn:
        query_parameters = (public_id,)
        query= '''
               DELETE FROM users
               WHERE public_id=%s
               '''
        conn.execute(query, query_parameters)
    return Response(status=200)


@app.route("/login", methods=['POST'], endpoint='login')
def login():
    data = request.get_json()
    if not data.get('mail') or not data.get('password'):
        return Response(status=400)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        query_parameters = (data['mail'],)
        query  = '''
                SELECT username, public_id, mail, password FROM users WHERE mail=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()

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
        query_parameters = (current_user, event_time)
        query = '''
                SELECT 1
                FROM smoked_cigarettes
                WHERE public_user_id=%s AND event_time=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()
    if result:
        return Response(status=400)

    with engine.begin() as conn:
        query_parameters = (current_user, event_time)
        query = '''
                INSERT INTO smoked_cigarettes (public_user_id, event_time)
                VALUES (%s, %s)
                '''
        conn.execute(query, query_parameters)

    return Response(status=201)


@app.route("/cigarettes", methods=['GET'], endpoint='get_cigarettes')
@token_requiered
def get_cigarettes(current_user):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        query_parameters = (current_user,)
        query = '''
                SELECT cigarette_id, event_time 
                FROM smoked_cigarettes 
                WHERE public_user_id=%s
                '''
        results = conn.execute(query, query_parameters)

    cigarettes = []
    for cigarette in results:
        cigarettes.append({
            'id': cigarette["cigarette_id"],
            'event_time': cigarette["event_time"].strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(cigarettes)


@app.route("/cigarette/<cigarette_id>", methods=['DELETE'], endpoint='delete_cigarette')
@token_requiered
def delete_cigarette(current_user, cigarette_id):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    with engine.connect() as conn:
        query_parameters = (cigarette_id, current_user)
        query = '''
                SELECT 1 
                FROM smoked_cigarettes 
                WHERE cigarette_id=%s and public_user_id=%s
                '''
        result = conn.execute(query, query_parameters).fetchone()
    if not result:
        return Response(status=404)

    with engine.begin() as conn:
        query_parameters = (cigarette_id, current_user)
        query = '''
                DELETE 
                FROM smoked_cigarettes 
                WHERE cigarette_id=%s and public_user_id=%s
                '''
        conn.execute(query, query_parameters)
    return Response(status=200)
