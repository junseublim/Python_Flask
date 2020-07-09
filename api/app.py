import config
from flask      import Flask
from flask_cors import CORS

#DB 연결 위한 데이터 베이스, create_engine을 사용하여 데이터베이스에 연결한다.
from sqlalchemy import create_engine

from model import UserDao, TweetDao
from service import UserService, TweetService
from view import create_endpoints


class Services:
    pass

#create_app은 팩토리 함수로, 자동으로 인식해서 Flask를 실행시킨다. test_config 인자는 단위 테스트를 실행시킬때 필요
def create_app(test_config = None):
    #import한 Flask 클래스 객체화시켜서 app에 저
    app = Flask(__name__)
    #CORS 문제 해결 위함
    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    database = create_engine(app.config['DB_URL'], encoding= 'utf-8', max_overflow = 0)

    user_dao = UserDao(database)
    tweet_dao = TweetDao(database)

    services = Services
    services.user_service = UserService(user_dao, app.config)
    services.tweet_service = TweetService(tweet_dao)

    create_endpoints(app, services)

    return app