db = {
    'user'     : 'root',
    'password' : '12341234',
    'host'     : 'marketholy-db.c29zw1eoxv4n.ap-northeast-2.rds.amazonaws.com',
    'port'     : '3306',
    'database' : 'brandi'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8" 