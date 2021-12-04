import datetime as dt
from main import db

class Log(db.Model):

    __tablename__ = 'users'

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