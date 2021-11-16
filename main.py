from flask import Flask,jsonify, request
from database import engine
from flask_jwt_extended import (JWTManager,
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required)
from security import authenticate, identity, users
from blacklist import BLACKLIST
from user import User
from leave import Leave
from log import Log

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config['JWT_SECRET_KEY'] = 'get_out'  # we can also use app.secret like before, Flask-JWT-Extended can recognize both
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)



leaves = [
    Leave(0,3,"2021-09-01", "2021-09-10", 2),
    Leave(1,2,"2021-06-05","2021-06-14",2),
    Leave(2,1,"2021-01-05", "2021-02-01", 1),
    Leave(3,0, "2021-01-05", "2021-01-14",1)
]


logs = [
    Log(1,1,"2021-09-01", 8.25),
    Log(2,1,"2021-09-06", 5),
    Log(3,2,"2021-09-06", 9)
]

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

@app.route("/timeoff/leaves")
@jwt_required()
def get_all_leaves():
    claims = get_jwt()
    returning_leaves = []
    if claims["level"]=="admin":
        for leave in leaves:
            returning_leaves.append(leave.to_dict())
        return jsonify(returning_leaves)
    elif claims["level"]=="user":
        user=claims["user_id"]
        for leave in leaves:
            if leave.user == user:
                returning_leaves.append(leave.to_dict())
        return jsonify(returning_leaves)
    elif claims["level"] == "tl":
        team = claims["team_id"]
        print(team)
        users_taken = []
        for user_lol in users:
            if(user_lol.team_id == team):
               users_taken.append(user_lol.id)
        for leave in leaves:
            if leave.user in users_taken:
                returning_leaves.append(leave.to_dict())
        return jsonify(returning_leaves)
    return {"message":"Not available"}, 401


@app.route("/timeoff/leaves", methods = ["POST"], endpoint = "add_leave") 
@jwt_required()
def add_leave():
    claims = get_jwt()
    user_id = claims["user_id"]
    request_data=request.get_json()
    new_leave = Leave(request_data["id"], user_id,request_data["start_date"],request_data["end_date"],request_data["type"] )
    leaves.append(new_leave)
    return new_leave.to_dict()


@app.route("/timeoff/leaves/<int:id>", methods = ["PUT"], endpoint = "update_leave")
@jwt_required()
def update_leave(id):
    request_data=request.get_json()
    claims = get_jwt()
    user_id= claims["user_id"]
    for leave in leaves:
        if leave.id == id :
            leave.start_date=request_data["start_date"]
            leave.end_date=request_data["end_date"]
            return leave.to_dict()
        # else:
        #     return {"message":"not allowed"}, 401
    return "No leave with that ID found",404


@app.route("/timeoff/leaves/<int:id>", endpoint = "get_leave")
@jwt_required()
def get_leave(id):
    for leave in leaves:
        if leave.id==id:
            return leave.to_dict()
    return "No leave with that ID found", 404


@app.route("/timeoff/leaves/<int:id>", methods = ["DELETE"], endpoint = "delete_leave")
@jwt_required()
def delete_leave(id):
    for leave in leaves:
        if leave.id==id:
            leaves.remove(leave)
            return {"message":"deleted"}
    return {"message":"not found"}, 404

# ----------------------------------------------------------------------------------------------------------------------

@app.route("/timein/logs", endpoint = "get_all_logs")
@jwt_required()
def get_all_logs():
    claims = get_jwt()
    returning_logs = []
    if claims["level"]=="admin":
        for log in logs:
            returning_logs.append(log.to_dict())
        return jsonify(returning_logs)
    elif claims["level"]=="user":
        user=claims["user_id"]
        for log in logs:
            if log.user == user:
                returning_logs.append(log.to_dict())
        return jsonify(returning_logs)
    elif claims["level"] == "tl":
        team = claims["team_id"]
        print(team)
        users_taken = []
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
    logs.append(new_log)
    return new_log.to_dict()


@app.route("/timein/logs/<int:id>", methods = ["PUT"], endpoint = "update_log")
@jwt_required()
def update_log(id):
    request_data=request.get_json()
    for log in logs:
        if log.id == id:
            log.date=request_data["date"]
            log.time_spent=request_data["time_spent"]
            return log.to_dict()
    return "No log with that ID found", 404



@app.route("/timein/logs/<int:id>", endpoint = "get_log")
@jwt_required()
def get_log(id):
    for log in logs:
        if log.id==id:
            return log.to_dict()
    return "No log with that ID found", 404


@app.route("/timein/logs/<int:id>", methods = ["DELETE"], endpoint = "delete_log")
@jwt_required()
def delete_log(id):
    for log in logs:
        if log.id==id:
            logs.remove(log)
            return {"message":"deleted"}
    return {"message":"not found"}, 404

# ----------------------------------------------------------------------------------------------------------------------

@app.route("/users", endpoint = "get_all_users")
@jwt_required()
def get_all_users():
    returning_users = []
    claims = get_jwt()
    if claims["level"]=="admin":
        for i in range(0,len(users)):
            returning_users.append(users[i].to_dict())
        return jsonify(returning_users)
    if claims["level"]=="tl":
        for i in range(len(users)):
            if(users[i].team_id == claims["team_id"]):
                returning_users.append(users[i].to_dict())
        return jsonify(returning_users)
    return {"message":"not an admin"}, 400

@app.route("/users", methods = ["POST"], endpoint = "add_user")
@jwt_required()
def add_user():
    claims = get_jwt()
    if claims["level"]=="admin":
        request_data = request.get_json()
        temp_user = User(request_data["user_level"],request_data["id"],
        request_data["team_id"],request_data["username"],
        request_data["job_coefficient"],request_data["password"])
        users.append(temp_user)
        return temp_user.to_dict()
    return {"message":"not and admin"}, 401

@app.route("/users/<int:id>", methods = ["PUT"], endpoint = "update_user")
@jwt_required()
def update_user(id):
    claims = get_jwt()
    if claims["level"]=="admin" :
        request_data=request.get_json()
        for user_lol in users:
            if user_lol.id == id:
                user_lol.name=request_data["name"]
                user_lol.job_coefficient=request_data["job_coefficient"]
                return user_lol.to_dict()
    elif claims["level"]=="user":
        request_data=request.get_json()
        for user_lol in users:
            if user_lol.id == id and user_lol.id == claims["user_id"]:
                user_lol.name=request_data["name"]
                user_lol.job_coefficient=request_data["job_coefficient"]
                return user_lol.to_dict()
    return {"message":"Can't do this operation"}, 404


@app.route("/users/<int:id>", endpoint = "get_user")
@jwt_required()
def get_user(id):
    if(get_jwt()["level"]=="admin"):
        for user in users:
            if user.id==id:
                return user.to_dict()
    if (get_jwt()["level"]=="tl" or get_jwt()["level"]=="user"): return {"message":"Not and admin"}
    return {"message":"No user with that ID found"}, 404



@app.route("/users/<int:id>", methods = ["DELETE"], endpoint = "delete_user")
@jwt_required()
def delete_user(id):
    claims = get_jwt()
    if claims["level"]=="admin":
        for user in users:
            if user.id==id:
                users.remove(user)
                return "deleted"
    return "not found", 404

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
    

if __name__=="__main__":
    app.run(port=5000)
