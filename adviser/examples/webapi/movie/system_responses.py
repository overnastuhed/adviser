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
        sys_act.add_value('id', movie['id'])
        sys_act.add_value('title', movie['title'])
        sys_act.add_value('overview', movie['overview'])
        sys_act.add_value('release_year', movie['release_year'])
        for genre in movie['genres']:
            sys_act.add_value('genres', genre)
        sys_act.add_value('cast', movie['cast'])
        sys_act.add_value('rating', movie['rating'])
        return sys_act

    def tell_user_about_movie(movie):
        #TODO: Smarter way to select which fields to tell to the user.
        sys_act = SysAct(SysActionType.InformByName)
        sys_act.add_value('id', movie['id'])
        sys_act.add_value('title', movie['title'])
        sys_act.add_value('overview', movie['overview'])
        sys_act.add_value('release_year', movie['release_year'])
        for genre in movie['genres']:
            sys_act.add_value('genres', genre)
        sys_act.add_value('cast', movie['cast'])
        sys_act.add_value('rating', movie['rating'])
        return sys_act