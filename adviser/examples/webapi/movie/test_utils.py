from utils.sysact import SysAct, SysActionType
from utils.useract import UserActionType
from utils.beliefstate import BeliefState
from .domain import MovieDomain

class SysActFactory():
    def __init__(self, actionType: SysActionType):
        self.sysact = SysAct(actionType)

    def id(self, text=None):
        self.sysact.add_value("artificial_id", text)
        return self
    
    def actor(self, text=None):
        self.sysact.add_value("with_actors", text)
        return self

    def genre(self, text=None):
        self.sysact.add_value("with_genres", text)
        return self

    def year(self, text=None):
        self.sysact.add_value("primary_release_year", text)
        return self

    def title(self, text=None):
        self.sysact.add_value("title", text)
        return self

    def cast(self, text=None):
        self.sysact.add_value("credits", text)
        return self

    def overview(self, text=None):
        self.sysact.add_value("overview", text)
        return self

    def build(self):
        return self.sysact


class BeliefStateFactory():
    def __init__(self):
        self.bs = BeliefState(MovieDomain())

    def inform(self, slot, value):
        self.bs['informs'][slot] = {value: 1.0}
        self.bs['user_acts'].add(UserActionType.Inform)
        return self

    def request(self, slot):
        self.bs['request'][slot] = 1.0
        self.bs['user_acts'].add(UserActionType.Request)
        return self

    def request_alternative(self):
        self.bs['user_acts'].add(UserActionType.RequestAlternatives)
        return self

    def build(self):
        return self.bs