import pytest
import bcrypt
import json
import config

from app import create_app                      #create_app 함수 import한다
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding= 'utf-8', max_overflow = 0)

def setup_function():
    #test가 실행되기 전에 이 함수가 자동으로 실행됨.
    hashed_password = bcrypt.hashpw(b"test123", bcrypt.gensalt())
    # 테스트 사용자 생성
    new_user = {
        'id' : 1,
        'email': 'junslim11@gmail.com',
        'hashed_password': hashed_password,
        'name': 'jun',
        'profile': 'test profile'
    }
    database.execute(text("""
        insert into users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) Values (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
            )
    """), new_user)

def teardown_function():
    database.execute(text("set foreign_key_checks=0"))
    database.execute(text("Truncate users"))
    database.execute(text("Truncate tweets"))
    database.execute(text("Truncate users_follow_list"))
    database.execute(text("set foreign_key_checks=1"))

@pytest.fixture #fixture데코레이터가 적용된 함수와 같은 이름의 인자가 다른 test 함수에
                # 지정되어 있으면 같은 이름의 함수의 리턴 값을 해당 인자로 넣어준다.
def api():  #fixture 함수 이름
    app = create_app(config.test_config) #테스트할 미니터 API 애플리케이션 생성
    app.config['TEST'] = True   #Flask가 에러가 났을 경우 http 요청 오류 부분은 핸들링하지 ㅇ낳음으로써 오류 메시지 출력되지 않게 한다.
    api = app.test_client() #테스트용 클라이언트를 생성한다. 이 클라이언트를 사용해서 원하는 엔드포인트들을 호출할 수 있게된다.

    return api

#ping 엔드포인트 테스트하는 함수. api인자는 pytest가 자동으로 인자를 넘겨준다.
def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_tweet(api):
    resp = api.post('/login', data = json.dumps({'email' : 'junslim11@gmail.com', 'password' : 'test123'}),content_type='application/json')
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    #tweet
    resp = api.post('/tweet', data=json.dumps({'tweet' : "Hello world!"}), content_type='application/json', headers={'Authorization' : access_token})
    assert resp.status_code == 200

    #tweet 확인
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id' : 1,
                'tweet' : "Hello world!"
            }
        ]
    }

def test_login(api):
    resp = api.post('/login', data = json.dumps({'email' : 'junslim11@gmail.com', 'password' : 'test123'}),content_type='application/json')
    assert b"access_token" in resp.data

def test_unauthorized(api):
    resp = api.post(
        '/tweet',
        data=json.dumps({'tweet': "Hello World!"}),
        content_type='application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/follow',
        data         = json.dumps({'follow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/unfollow',
        data         = json.dumps({'unfollow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401
