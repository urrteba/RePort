import datetime as dt

class Leave:
    def __init__(self,_id:int, user_id:int, start_date:str, end_date:str, type:int):
        self.id:int = _id
        self.user:int = user_id
        self.start_date:str = start_date
        self.end_date : str = end_date
        self.type : int = type  #1-vacation 2-sickness

    def check_dates(self):
        start = dt.strptime(self.start_date, "%Y-%m-%d")
        end = dt.strptime(self.end_date, "%Y-%m-%d")
        if end > start:
            return True
        return False
    
    def to_dict(self):
        return {
            "leave_id":self.id,
            "user_id": self.user,
            "start":self.start_date,
            "end":self.end_date,
            "type":self.type
        }
