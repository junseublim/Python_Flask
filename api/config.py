db = {
    'user' : 'root',
    'password' : 'password',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'miniter'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

#테스트 데이터베이스 접속 설정 지정해준다
test_db = {
    'user' : 'root',
    'password' : 'password',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'miniter_test'
}
#지정해둔 데이터베이스 접속 설정을 기반으로 접속 url을 test_config이라는 딕셔너리에 저장
test_config = {
    'DB_URL' : f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY': 'SOME_SUPER_SECRET_KEY',
    'JWT_EXP_DELTA_SECONDS': 7 * 24 * 60 * 60
}

JWT_SECRET_KEY = 'SOME_SUPER_SECRET_KEY'