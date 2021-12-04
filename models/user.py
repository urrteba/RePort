import datetime as dt
from main import db

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    user_level = db.Column(db.Integer)
    name = db.Column(db.String(80))
    job_coefficient = db.Column(db.Integer)
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
