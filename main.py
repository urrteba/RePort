from flask import Flask,jsonify, request
from database import engine
app = Flask(__name__)

leaves = [
    {
        "id" : 1,
        "user":"Lol",
        "start_date":"2021-09-01",
        "end_date":"2021-09-10"
    },
    {
        "id":2,
        "user":"N/a",
        "start_date":"2021-01-01",
        "end_date":"2021-06-25"
    }
]

users = [
    {
        "id":1,
        "name":"user",
        "job_coefficient":1
    },
    {
        "id":2,
        "name":"jonas",
        "job_coefficient":2
    }
]

logs = [
    {
        "id":1,
        "date":"2021-09-01",
        "time_spent":8.25,
        "user":1
    },
    {
        "id":2,
        "date":"2021-09-06",
        "time_spent":5,
        "user":1
    },
    {
        "id": 3,
        "date": "2021-09-06",
        "time_spent": 9,
        "user": 2
    }
]

@app.route("/")
def home():
    return "Welcome to RePorts"

#-----------------------------------------------------------------------------------------------------------------------

@app.route("/timeoff/leaves")
def get_all_leaves():
    return jsonify(leaves)

@app.route("/timeoff/add_leave/", methods = ["POST"])  #{user:, leave_type:, leave_date:}
def add_leave():
    request_data=request.get_json()
    new_leave = {
        "id":request_data["id"],
        "user":request_data["user"],
        "start_date":request_data["start_date"],
        "end_date":request_data["end_date"]
    }
    leaves.append(new_leave)
    return new_leave


@app.route("/timeoff/update/<int:id>", methods = ["PUT"])
def update_leave(id):
    request_data=request.get_json()
    for leave in leaves:
        if leave["id"] == request_data["id"]:
            leave["start_date"]=request_data["start_date"]
            leave["end_date"]=request_data["end_date"]
            return leave
    return "No leave with that ID found"

@app.route("/timeoff/<int:id>")
def get_leave(id):
    for leave in leaves:
        if leave["id"]==id:
            return jsonify(leave)
    return "No leave with that ID found"

@app.route("/timeoff/delete/<int:id>", methods = ["DELETE"])
def delete_leave(id):
    for leave in leaves:
        if leave["id"]==id:
            leaves.remove(leave)
            return "deleted"
    return "not found"

# ----------------------------------------------------------------------------------------------------------------------
@app.route("/timein/logs")
def get_all_logs():
    return jsonify(logs)

@app.route("/timein/add_log", methods = ["POST"])
def add_log():
    request_data = request.get_json()
    new_log = {
        "id": request_data["id"],
        "user": request_data["user"],
        "time_spent": request_data["time_spent"],
        "date": request_data["date"]
    }
    logs.append(new_log)
    return new_log

@app.route("/timein/logs/<int:id>", methods = ["PUT"])
def update_log(id):
    request_data=request.get_json()
    for log in logs:
        if log["id"] == id:
            log["date"]=request_data["date"]
            log["time_spent"]=request_data["time_spent"]
            return log
    return "No log with that ID found"

@app.route("/timein/<int:id>")
def get_log(id):
    for log in logs:
        if log["id"]==id:
            return jsonify(log)
    return "No log with that ID found"

@app.route("/timein/delete/<int:id>", methods = ["DELETE"])
def delete_log(id):
    for log in logs:
        if log["id"]==id:
            logs.remove(log)
            return "deleted"
    return "not found"

# ----------------------------------------------------------------------------------------------------------------------
@app.route("/users")
def get_all_users():
    return jsonify(users)

@app.route("/users/add", methods = ["POST"])
def add_user():
    request_data = request.get_json()
    new_user = {
        "id": request_data["id"],
        "name": request_data["name"],
        "job_coefficient":request_data["job_coefficient"]
    }
    users.append(new_user)
    return new_user

@app.route("/users/update/<int:id>", methods = ["PUT"])
def update_user(id):
    request_data=request.get_json()
    for user in users:
        if user["id"] == id:
            user["name"]=request_data["name"]
            user["job_coefficient"]=request_data["job_coefficient"]
            return user
    return "No user with that ID found"

@app.route("/users/<int:id>")
def get_user(id):
    for user in users:
        if user["id"]==id:
            return jsonify(user)
    return "No user with that ID found"

@app.route("/users/delete/<int:id>", methods = ["DELETE"])
def delete_user(id):
    for user in users:
        if user["id"]==id:
            users.remove(user)
            return "deleted"
    return "not found"

#-----------------------------------------------------------------------------------------------------------------------
if __name__=="__main__":
    app.run(port=5000)
