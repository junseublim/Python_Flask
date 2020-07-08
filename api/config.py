db = {
    'user' : 'admin',
    'password' : 'mysql1113',
    'host' : 'database-1.cyb683fyyxlz.ap-northeast-2.rds.amazonaws.com',
    'port' : 3306,
    'database' : 'database-1'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

JWT_SECRET_KEY = 'SOME_SUPER_SECRET_KEY'