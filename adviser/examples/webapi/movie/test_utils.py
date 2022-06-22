from utils.sysact import SysAct, SysActionType

class SysActFactory():
    def __init__(self, actionType: SysActionType):
        self.sysact = SysAct(actionType)
    
    def actor(self, text):
        self.sysact.add_value("with_actors", text)
        return self

    def genre(self, text):
        self.sysact.add_value("with_genres", text)
        return self

    def year(self, text):
        self.sysact.add_value("primary_release_year", text)
        return self

    def title(self, text):
        self.sysact.add_value("title", text)
        return self

    def cast(self, text):
        self.sysact.add_value("credits", text)
        return self

    def overview(self, text):
        self.sysact.add_value("overview", text)
        return self

    def build(self):
        return self.sysact