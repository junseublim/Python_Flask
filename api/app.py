import jwt
import bcrypt

from flask      import Flask, request, jsonify, current_app, Response, g
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
from datetime   import datetime, timedelta
from functools  import wraps

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)

def create_app(test_config=None):
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt())
        new_user_id = app.database.execute(text("""
            Insert into users (
            name,
            email,
            profile,
            hashed_password
            ) values (
            :name,
            :email,
            :profile,
            :password
            )
        """), new_user).lastrowid
        row = app.database.execute(text("""
            select
            id,
            name,
            email,
            profile
            from users
            where id = :user_id
        """), {
            'user_id': new_user_id
        }).fetchone()

        created_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(created_user);

    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet['user_id'] = g.user_id
        tweet = user_tweet["tweet"]
        if len(tweet) > 300:
            return '300자 초과', 400
        app.database.execute(text("""
        insert into tweets (
            user_id,
            tweet
            ) values (
            :user_id,
            :tweet
            )
        """), user_tweet)
        return '', 200

    @app.route("/login", methods=['POST'])
    def login():
        credential = request.json
        email = credential['email']
        password = credential["password"]
        row = app.database.execute(text("""
            select
                id,
                hashed_password
            from users
            where email = :email
        """), {'email': email}).fetchone()
        if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
            user_id = row['id'];
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'],
                               'HS256')
            return jsonify({
                'access_token': token.decode('UTF-8')
            })
        else:
            return '', 401

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        rows = app.database.execute(text("""
               select
               t.user_id,
               t.tweet
               from tweets t
               left join users_follow_list ufl on ufl.user_id = :user_id
               where t.user_id = :user_id
               or t.user_id = ufl.follow_user_id
           """), {
            'user_id': user_id
        }).fetchall()

        timeline = [{
            'user_id': row['user_id'],
            'tweet': row['tweet']
        } for row in rows]

        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })

    @app.route("/users", methods=["GET"])
    def users():
        userlist = app.database.execute(text("""
        select
            name
        from users
        """)).fetchall()
        usernames = [{
            'name': user['name']
        } for user in userlist]
        return jsonify({
            'usernames': usernames
        })

    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        new_follow = request.json;
        app.database.execute(text("""
                    Insert into users_follow_list (
                    user_id,
                    follow_user_id
                    ) values (
                    :user_id,
                    :follow_user_id
                    )
                """), new_follow)
        row = app.database.execute(text("""
                    select
                    user_id,
                    follow_user_id
                    from users_follow_list
                    where user_id = :user_id and follow_user_id = :follow_user_id
                """), new_follow).fetchone()

        following = {
            'id': row['user_id'],
            'following': row['follow_user_id']
        } if row else None

        return jsonify(following);

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        new_unfollow = request.json;
        app.database.execute(text("""
                            delete from users_follow_list
                            where user_id = :user_id and follow_user_id = :follow_user_id
                        """), new_unfollow)
        rows = app.database.execute(text("""
                            select
                            user_id,
                            follow_user_id
                            from users_follow_list
                            where user_id = :user_id
                        """), new_unfollow).fetchall()
        following = [{
            'id': row['user_id'],
            'following': row['follow_user_id']
        } for row in rows]
        return jsonify(following);

    return app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None
            if payload is None: return Response(status=401)

            user_id = payload['user_id']
            g.user_id = user_id
            g.user = get_user_info(user_id) if user_id else None
        else:
            return Response(status=401)
        return f(*args, **kwargs)
    return decorated_function

def get_user_info(user_id):
    user = current_app.database.execute(text("""
           select
               id, name, email, profile
           from users
           where id = :user_id
           """), {'user_id': user_id}).fetchone()
    return {
        'id' : user['id'],
        'name': user['name'],
        'email': user['email'],
        'profile': user['profile'],
    } if user else None
