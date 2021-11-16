import datetime as dt

class Log:

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