from utils.sysact import SysAct, SysActionType
from utils.useract import UserActionType
from utils.beliefstate import BeliefState
from .domain import MovieDomain

class SysActFactory():
    def __init__(self, actionType: SysActionType):
        self.sysact = SysAct(actionType)

    def id(self, text=None, any=False):
        self.sysact.add_value("id", text if not any else '*')
        return self
    
    def actor(self, text=None, any=False):
        self.sysact.add_value("cast", text if not any else '*')
        return self

    def genre(self, text=None, any=False, containing=None):
        if containing:
            if not type(containing) == list:
                containing = [containing]
            for genre in containing:
                self.sysact.add_value("genres", genre)
            self.sysact.add_value("genres", '*')
        else:
            self.sysact.add_value("genres", text if not any else '*')
        return self

    def year(self, text=None, any=False):
        self.sysact.add_value("release_year", text if not any else '*')
        return self

    def title(self, text=None, any=False):
        self.sysact.add_value("title", text if not any else '*')
        return self

    def overview(self, text=None, any=False):
        self.sysact.add_value("overview", text if not any else '*')
        return self

    def rating(self, text=None, any=False):
        self.sysact.add_value("rating", text if not any else '*')
        return self

    def confirm(self, question):
        self.sysact.add_value('confirm', question)
        return self
    
    def result_count(self, count=None, any=False):
        self.sysact.add_value('num_results', count if not any else '*')
        return self

    def build(self):
        return self.sysact


class BeliefStateFactory():
    def __init__(self):
        self.bs = BeliefState(MovieDomain())
        self.bs.start_new_turn()

    def inform(self, slot, value):
        if type(value) == list:
            self.bs['informs'][slot] = {}
            for v in value:
                self.bs['informs'][slot][v] = 1.0
        else:
            self.bs['informs'][slot] = {value: 1.0}
        self.bs['user_acts'].add(UserActionType.Inform)
        return self

    def request(self, slot):
        self.bs['requests'][slot] = 1.0
        self.bs['user_acts'].add(UserActionType.Request)
        return self

    def request_alternative(self):
        self.bs['user_acts'].add(UserActionType.RequestAlternatives)
        return self

    def affirm(self):
        self.bs['user_acts'].add(UserActionType.Affirm)
        return self

    def deny(self):
        self.bs['user_acts'].add(UserActionType.Deny)
        return self

    def bye(self):
        self.bs['user_acts'].add(UserActionType.Bye)
        return self

    def new_turn(self, taken_sys_act = None):
        if taken_sys_act:
            self.bs['sys_act'] = taken_sys_act
        self.bs.start_new_turn()
        self.bs['requests'] = {}
        self.bs['user_acts'] = set()
        return self

    def build(self):
        return self.bs