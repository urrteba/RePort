import os
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,jsonify, request
from flask_jwt_extended import (JWTManager,
    create_access_token,
    get_jwt,
    jwt_required)
from blacklist import BLACKLIST
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:developer@localhost/postgres')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dyqcnffzbpsggq:222fe62fb4726221f1dac9273d066a25895908d0521131f9b29f6d5ca8779c1e@ec2-18-213-133-45.compute-1.amazonaws.com:5432/d9bkms8k27dsnf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:developer@localhost/postgres'
app.config['SQL_ALCHEMY_MODIFICATIONS'] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config['JWT_SECRET_KEY'] = 'get_out'
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------------------------------------------------
class User(db.Model):

    __tablename__ = 'users'
    # __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key = True)
    user_level = db.Column(db.Integer)
    name = db.Column(db.String(80))
    job_coefficient = db.Column(db.Float(precision = 2))
    password = db.Column(db.String(80))
    team_id = db.Column(db.Integer)

    def __init__(self,user_type:int,id:int,team_id:int, name:str, job_coefficient : float, password:str):
        self.id = id
        self.user_level = user_type
        self.name = name
        self.job_coefficient = job_coefficient
        self.password = password
        self.team_id = team_id

    def to_dict(self):
        return {
            "id" : self.id,
            "user_level":self.user_level,
            "name":self.name,
            "coefficient":self.job_coefficient,
            "team":self.team_id
        }
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(name=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

class Leave(db.Model):
    __tablename__ = 'leaves'
    # __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer)
    start_date = db.Column(db.String(80))
    end_date = db.Column(db.String(80))
    type = db.Column(db.Integer)

    def __init__(self, _id: int, user_id: int, start_date: str, end_date: str, type: int):
        self.id: int = _id
        self.user: int = user_id
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.type: int = type  # 1-vacation 2-sickness

    def check_dates(self):
        start = dt.strptime(self.start_date, "%Y-%m-%d")
        end = dt.strptime(self.end_date, "%Y-%m-%d")
        if end > start:
            return True
        return False

    def to_dict(self):
        return {
            "leave_id": self.id,
            "user_id": self.user,
            "start": self.start_date,
            "end": self.end_date,
            "type": self.type
        }

class Log(db.Model):

    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer)
    date = db.Column(db.String(80))
    time_spent = db.Column(db.Float(precision = 2))


    def __init__(self,_id:int, user:int, date:str, time_spent: float):
        self.id = _id
        self.user = user
        self.date = date
        self.time_spent=time_spent

    def to_dict(self):
        return {
            "id":self.id,
            "user":self.user,
            "date":self.date,
            "time_spent":self.time_spent
        }

# ----------------------------------------------------------------------------------------------------------------------

# leaves = [
#     Leave(0,3,"2021-09-01", "2021-09-10", 2),
#     Leave(1,2,"2021-06-05","2021-06-14",2),
#     Leave(2,1,"2021-01-05", "2021-02-01", 1),
#     Leave(3,0, "2021-01-05", "2021-01-14",1)
# ]
#
# users = [
#     User(0,0,0, 'admin',1,'admin'),
#     User(1,1,1, 'user1', 0.75,'user1'),
#     User(1,2,1, 'user2', 0.5,'user2'),
#     User(2,3,1,"tl", 1,"tl")
# ]
#
# logs = [
#     Log(1,1,"2021-09-01", 8.25),
#     Log(2,1,"2021-09-06", 5),
#     Log(3,2,"2021-09-06", 9)
# ]

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 0:
        return {"level":"admin"}
    elif identity == 1:
        return {"level":"user"}
    else:
        return {"level":"tl"}


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST
#----------------------------------------------------------------------------------------------------------------------

@app.route("/")
def home():
    return "Welcome to RePorts"

#-----------------------------------------------------------------------------------------------------------------------
#
@app.route("/timeoff/leaves")
@jwt_required()
def get_all_leaves():
    claims = get_jwt()
    returning_leaves = []
    if claims["level"]=="admin":
        try:
            returning_leaves = Leave.query.all()
            return jsonify([l.to_dict() for l in returning_leaves])
        except Exception as e:
            return (str(e))
        # return jsonify(returning_leaves)
    elif claims["level"]=="user":
        user=claims["user_id"]
        returning_leaves = Leave.query.filter_by(user = user)
        return jsonify([l.to_dict() for l in returning_leaves])
    elif claims["level"] == "tl":
        team = claims["team_id"]
        users = User.query.all()
        leaves = Leave.query.all()
        users_taken = []
        for user_lol in users:
            if(user_lol.team_id == team):
               users_taken.append(user_lol.id)
        for leave in leaves:
            if leave.user in users_taken:
                returning_leaves.append(leave.to_dict())
        return jsonify(returning_leaves)
    return {"message":"Not available"}, 401

#
@app.route("/timeoff/leaves", methods = ["POST"], endpoint = "add_leave")
@jwt_required()
def add_leave():
    claims = get_jwt()
    user_id = claims["user_id"]
    request_data=request.get_json()
    new_leave = Leave(request_data["id"], user_id,request_data["start_date"],request_data["end_date"],request_data["type"] )
    db.session.add(new_leave)
    db.session.commit()
    return new_leave.to_dict()


@app.route("/timeoff/leaves/<int:id>", methods = ["PUT"], endpoint = "update_leave")
@jwt_required()
def update_leave(id):
    request_data=request.get_json()
    claims = get_jwt()
    user_id= claims["user_id"]
    leave = Leave.query.filter_by(id = id).first()
    # print(type(leave))
    if leave:
        if leave.user == user_id:
            leave.start_date=request_data["start_date"]
            leave.end_date=request_data["end_date"]
            db.session.commit()
            return leave.to_dict()
        return {"message":"not your own leave, can't update"}, 401
    return {"message":"No leave with that ID found"},404


@app.route("/timeoff/leaves/<int:id>", endpoint = "get_leave")
@jwt_required()
def get_leave(id):
    leave = Leave.query.filter_by(id = id)
    if leave:
        return leave.to_dict()
    return "No leave with that ID found", 404


@app.route("/timeoff/leaves/<int:id>", methods = ["DELETE"], endpoint = "delete_leave")
@jwt_required()
def delete_leave(id):
    leave = Leave.query.filter_by(id = id).first()
    if leave:
        db.session.delete(leave)
        db.session.commit()
        return {"message":"deleted"}
    return {"message":"not found"}, 404

# # ----------------------------------------------------------------------------------------------------------------------

@app.route("/timein/logs", endpoint = "get_all_logs")
@jwt_required()
def get_all_logs():
    claims = get_jwt()
    returning_logs = []
    if claims["level"]=="admin":
        returning_logs = Log.query.all()
        return jsonify([retlog.to_dict() for retlog in returning_logs])
    elif claims["level"]=="user":
        user=claims["user_id"]
        returning_logs = Log.query.filter_by(user = user)
        return jsonify([retlog.to_dict() for retlog in returning_logs])
    elif claims["level"] == "tl":
        team = claims["team_id"]
        users_taken = []
        users = User.query.all()
        logs = Log.query.all()
        for user_lol in users:
            if(user_lol.team_id == team):
               users_taken.append(user_lol.id)
        for log in logs:
            if log.user in users_taken:
                returning_logs.append(log.to_dict())
        return jsonify(returning_logs)
    return {"message":"Not available"}, 401


@app.route("/timein/logs", methods = ["POST"], endpoint = "add_log")
@jwt_required()
def add_log():
    request_data = request.get_json()
    new_log = Log(request_data["id"], get_jwt()["user_id"],
        request_data["date"],request_data["time_spent"])
    db.session.add(new_log)
    db.session.commit()
    return new_log.to_dict()


@app.route("/timein/logs/<int:id>", methods = ["PUT"], endpoint = "update_log")
@jwt_required()
def update_log(id):
    request_data=request.get_json()
    log = Log.query.filter_by(id = id).first()
    if log:
        log.date=request_data["date"]
        log.time_spent=request_data["time_spent"]
        db.session.commit()
        return log.to_dict()
    return "No log with that ID found", 404



@app.route("/timein/logs/<int:id>", endpoint = "get_log")
@jwt_required()
def get_log(id):
    log = Log.query.filter_by(id = id).first()
    if log:
        return log.to_dict()
    return {"message":"No log with that ID found"}, 404


@app.route("/timein/logs/<int:id>", methods = ["DELETE"], endpoint = "delete_log")
@jwt_required()
def delete_log(id):
    log = Log.query.filter_by(id=id).first()
    if log:
        db.session.delete(log)
        db.session.commit()
        return {"message":"deleted"}
    return {"message":"not found"}, 404

# # ----------------------------------------------------------------------------------------------------------------------

@app.route("/users", endpoint = "get_all_users")
@jwt_required()
def get_all_users():
    returning_users = []
    claims = get_jwt()
    if claims["level"]=="admin":
        returning_users = User.query.all()
        return jsonify([retus.to_dict() for retus in returning_users])
    if claims["level"]=="tl":
        team_id = claims["team_id"]
        returning_users = User.query.filter_by(team_id = claims["team_id"])
        return jsonify([retus.to_dict() for retus in returning_users])
    return {"message":"not an admin nor a team-lead"}, 400

@app.route("/users", methods = ["POST"], endpoint = "add_user")
@jwt_required()
def add_user():
    claims = get_jwt()
    if claims["level"]=="admin":
        request_data = request.get_json()
        try:
            temp_user = User(request_data["user_level"],request_data["id"],
            request_data["team_id"],request_data["username"],
            request_data["job_coefficient"],request_data["password"])
            db.session.add(temp_user)
            db.session.commit()
            return temp_user.to_dict()
        except Exception as e:
            return jsonify(str(e))
    return {"message":"not and admin"}, 401

@app.route("/users/<int:id>", methods = ["PUT"], endpoint = "update_user")
@jwt_required()
def update_user(id):
    claims = get_jwt()
    if claims["level"]=="admin" :
        request_data=request.get_json()
        user_lol = User.query.filter_by(id=id).first()
        if user_lol:
            user_lol.name=request_data["name"]
            user_lol.job_coefficient=request_data["job_coefficient"]
            db.session.commit()
            return user_lol.to_dict()
    elif claims["level"]=="user" or claims["level"] == "tl":
        request_data=request.get_json()
        user_lol = User.query.filter_by(id = id).first
        if user_lol and user_lol.id == claims["user_id"]:
            user_lol.name=request_data["name"]
            user_lol.job_coefficient=request_data["job_coefficient"]
            db.session.commit()
            return user_lol.to_dict()
    return {"message":"Can't do this operation"}, 404


@app.route("/users/<int:id>", endpoint = "get_user")
@jwt_required()
def get_user(id):
    if(get_jwt()["level"]=="admin"):
        user = User.query.filter_by(id=id).first()
        return user.to_dict()
    if (get_jwt()["level"]=="tl" or get_jwt()["level"]=="user" and get_jwt["user_id"] == id):
        return User.query.filter_by(id=id).first().to_dict()
    return {"message":"No user with that ID found"}, 404

@app.route("/users/<int:id>", methods = ["DELETE"], endpoint = "delete_user")
@jwt_required()
def delete_user(id):
    claims = get_jwt()
    if claims["level"]=="admin":
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return "deleted"
        return "not found", 404
    return {"message":"not and admin"}, 400

#-----------------------------------------------------------------------------------------------------------------------
@app.route("/login", methods = ["POST"], endpoint = "login")
def login():
    request_data=request.get_json()
    user = authenticate(request_data["username"], request_data["password"])
    if user :
        additional_claims = {"user_id":user.id, "team_id":user.team_id}
        access_token = create_access_token(identity = user.user_level, additional_claims=additional_claims)
        return {"access_token":access_token}, 200
    return {"message":"no user found, check credentials"}, 400

@app.route("/logout", methods = ["POST"], endpoint = "logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return {"message":"logged out successfully"}, 200

# username_table = {u.name: u for u in users}
# userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = User.find_by_username(username)
    # print(User.query.all())
    if user and password == user.password:
        return user

def identity(payload):
    user_id = payload['identity']
    return User.find_by_id(user_id)


if __name__=="__main__":
    db.create_all()
    app.run(port=5000)
