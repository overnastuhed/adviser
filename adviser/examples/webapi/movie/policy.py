import sys
from typing import List, Dict
from random import choice
from .system_responses import SystemResponses

from services.service import PublishSubscribe, Service

from utils import SysAct, SysActionType
from utils.beliefstate import BeliefState
from utils.useract import UserActionType

from utils.logger import DiasysLogger
from utils.domain.lookupdomain import LookupDomain

class MoviePolicy(Service):

    def __init__(self, domain: LookupDomain, logger: DiasysLogger = DiasysLogger()):
        Service.__init__(self, domain=domain)
        self.logger = logger

    @PublishSubscribe(sub_topics=["beliefstate"], pub_topics=["sys_act"])
    def choose_sys_act(self, beliefstate: BeliefState = None) -> dict(sys_act=SysAct):   
        user_actions = beliefstate["user_acts"]  
        user_taking_no_action = not user_actions
        is_first_turn = beliefstate.is_first_turn()
        if is_first_turn and user_taking_no_action:
            sys_act = SystemResponses.welcome()
        elif UserActionType.Bad in user_actions:
            sys_act = SystemResponses.bad()
        elif UserActionType.Bye in user_actions:
            sys_act = SystemResponses.bye()
        # if user only says thanks, ask if they want anything else
        elif UserActionType.Thanks in user_actions:
            sys_act = SystemResponses.ask_if_user_needs_something_else()
        # If user only says hello, request a random slot to move dialog along
        elif UserActionType.Hello in user_actions:
            #TODO: ask user what they want to do, give a hint as to what can be done
            slot = self._get_open_slot(beliefstate)
            sys_act = SystemResponses.ask_user_to_inform_about_a_slot(slot)
        else:
            sys_act = self._get_domain_specific_action(beliefstate)

        self.logger.dialog_turn("System Action: " + str(sys_act))

        return {'sys_act': sys_act}


    def _get_domain_specific_action(self, beliefstate: BeliefState):
        """Determines the next system action based on the current belief state and
           previous action.

           When implementing a new type of policy, this method MUST be rewritten

        Args:
            belief_state (HandCraftedBeliefState): system values on liklihood
            of each possible state

        Return:
            (SysAct): the next system action

        --LV
        """
        user_actions = beliefstate["user_acts"]  

        if UserActionType.Request in user_actions:
            return self._user_is_requesting_a_field(beliefstate)
        elif UserActionType.RequestAlternatives in user_actions:
            return self._user_is_asking_for_alternative(beliefstate)
        elif UserActionType.RequestRecommendation in user_actions:
            return self._user_is_asking_for_a_recommendation(beliefstate)
        else: 
            return self._user_is_looking_for_a_specific_movie(beliefstate)

    def _user_is_requesting_a_field(self, beliefstate):
        constraints = self._get_constraints(beliefstate)
        requested_field = self._get_requests(beliefstate)
        results = self.domain.query(constraints)
        if len(results) == 0:
            return SystemResponses.nothing_found()
        elif len(results) == 1:
            if requested_field in results[0]:
                return SystemResponses.tell_user_about_requested_slot(requested_field, results[0][requested_field])
            else:
                return SystemResponses.tell_user_data_couldnt_be_found(requested_field)
        elif len(results) <= 3:
            return SystemResponses.ask_user_to_pick_from_multiple_results(results)
        else:
            slot = self._get_open_slot(beliefstate)
            if slot:
                return SystemResponses.ask_user_to_inform_about_a_slot(slot)
            else: # Too many results, no open slot to ask user about, so ask user to pick one of the found movies
                return SystemResponses.ask_user_to_pick_from_multiple_results(results[0:3])

    def _user_is_asking_for_alternative(self, beliefstate):
        constraints = self._get_constraints(beliefstate)
        results = self.domain.query(constraints)
    
        movies_already_shown_to_user = self._get_already_shown_movies(beliefstate)

        for result in results:
            if result['id'] not in movies_already_shown_to_user:
                return SystemResponses.tell_user_about_movie(result)
        return SystemResponses.nothing_found()

    def _user_is_asking_for_a_recommendation(self, beliefstate):
        constraints = self._get_constraints(beliefstate)
        results = self.domain.query(constraints)
        if len(results) == 0:
            return SystemResponses.nothing_found()
        else:
            recommendation = results[0]
            return SystemResponses.recommend_movie(recommendation)

    def _user_is_looking_for_a_specific_movie(self, beliefstate):
        constraints = self._get_constraints(beliefstate)
        results = self.domain.query(constraints)
        if len(results) == 0:
            return SystemResponses.nothing_found()
        elif len(results) == 1:
            return SystemResponses.tell_user_about_movie(results[0])
        elif len(results) <= 3:
            return SystemResponses.ask_user_to_pick_from_multiple_results(results)
        else:
            slot = self._get_open_slot(beliefstate)
            if slot:
                return SystemResponses.ask_user_to_inform_about_a_slot(slot)
            else: # Too many results, no open slot to ask user about, so ask user to pick one of the found movies
                return SystemResponses.ask_user_to_pick_from_multiple_results(results[0:3])

    def _get_constraints(self, beliefstate):
        return beliefstate['informs']

    def _get_requests(self, beliefstate):
        return list(beliefstate['requests'].keys())[0]

    def _get_open_slot(self, beliefstate):
        current_constraints = self._get_constraints(beliefstate)
        for slot in self.domain.get_system_requestable_slots():
            if slot not in current_constraints:
                return slot
        return None

    def _get_already_shown_movies(self, beliefstate):
        shown_movie_ids = []
        for turn in beliefstate._history:
            if 'sys_act' not in turn:
                continue
            sys_act = turn['sys_act']
            if sys_act.type == SysActionType.InformByName or \
               sys_act.type == SysActionType.InformByAlternatives or \
               sys_act.type == SysActionType.ShowRecommendation:
                shown_movie_ids.append(sys_act.slot_values['id'][0])
                
        return shown_movie_ids