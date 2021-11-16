from werkzeug.security import safe_str_cmp
from user import User

users = [
    User(0,0,0, 'admin',1,'admin'),
    User(1,1,1, 'user1', 0.75,'user1'),
    User(1,2,1, 'user2', 0.5,'user2'),
    User(2,3,1,"tl", 1,"tl")
]

username_table = {u.name: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)
