import datetime as dt

class User:

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
