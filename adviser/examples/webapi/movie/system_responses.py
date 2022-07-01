from utils.sysact import SysAct, SysActionType

class SystemResponses: 
    def welcome():
        return SysAct(SysActionType.Welcome)

    def bad():
        return SysAct(SysActionType.Bad)

    def bye():
        return SysAct(SysActionType.Bye)

    def ask_if_user_needs_something_else():
        return SysAct(SysActionType.RequestMore)

    def ask_user_to_inform_about_a_slot(slot):
        sys_act = SysAct(SysActionType.Request)
        sys_act.add_value(slot, None)
        return sys_act

    def nothing_found():
        return SysAct(SysActionType.NothingFound)

    def tell_user_about_requested_slot(requested_slot, value):
        sys_act = SysAct(SysActionType.InformByName)
        sys_act.add_value(requested_slot, value)
        return sys_act

    def tell_user_data_couldnt_be_found(requested_slot):
        sys_act = SysAct(SysActionType.NothingFound)
        sys_act.add_value(requested_slot, None)
        return sys_act

    def ask_user_to_pick_from_multiple_results(results):
        sys_act = SysAct(SysActionType.InformByAlternatives)
        sys_act.add_value('titles', [result['title'] for result in results])
        return sys_act

    def recommend_movie(movie):
        sys_act = SysAct(SysActionType.ShowRecommendation)
        _add_values_to_sys_act(sys_act, movie)
        return sys_act

    def tell_user_about_movie(movie):
        #TODO: Smarter way to select which fields to tell to the user.
        sys_act = SysAct(SysActionType.InformByName)
        _add_values_to_sys_act(sys_act, movie)
        return sys_act



def _add_values_to_sys_act(sys_act, movie, slots=None):
    if slots is None:
        slots = ['id', 'title', 'overview', 'release_year', 'genres', 'cast', 'rating']
    for slot in slots:
        if slot in movie:
            if type(movie[slot]) == list:
                for value in movie[slot]:
                    sys_act.add_value(slot, value)
            else: 
                sys_act.add_value(slot, movie[slot])