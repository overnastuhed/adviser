from typing import List, Dict
from random import choice


from services.policy.policy_api import HandcraftedPolicy
from services.service import PublishSubscribe, Service

from utils import SysAct, SysActionType
from utils.beliefstate import BeliefState
from utils.useract import UserActionType

from utils.logger import DiasysLogger
from utils.domain.lookupdomain import LookupDomain



class MoviePolicy(HandcraftedPolicy):

    def __init__(self, domain: LookupDomain, logger: DiasysLogger = DiasysLogger()):
        """
        Initializes the policy

        Arguments:
            domain {domain.lookupdomain.LookupDomain} -- Domain

        """
        self.first_turn = True
        Service.__init__(self, domain=domain)
        self.last_action = None
        self.current_suggestions = []  # list of current suggestions
        self.s_index = 0  # the index in current suggestions for the current system reccomendation
        self.domain_key = domain.get_primary_key()
        self.logger = logger
        self.random = False

    @PublishSubscribe(sub_topics=["beliefstate"], pub_topics=["sys_act"])
    def choose_sys_act(self, beliefstate: BeliefState = None) -> dict(sys_act=SysAct):

        """
            Responsible for walking the policy through a single turn. Uses the current user
            action and system belief state to determine what the next system action should be.

            To implement an alternate policy, this method may need to be overwritten

            Args:
                belief_state (BeliefState): a BeliefState object representing current system
                                           knowledge
            Returns:
                (dict): a dictionary with the key "sys_act" and the value that of the systems next
                        action

        """
        # variables for general (non-domain specific) actions
        self._remove_gen_actions(beliefstate)

        # do nothing on the first turn --LV
        if self.first_turn and not beliefstate['user_acts']:
            self.first_turn = False
            sys_act = SysAct()
            sys_act.type = SysActionType.Welcome
            return {'sys_act': sys_act}
        elif UserActionType.Bad in beliefstate["user_acts"]:
            sys_act = SysAct()
            sys_act.type = SysActionType.Bad
        # if the action is 'bye' tell system to end dialog
        elif UserActionType.Bye in beliefstate["user_acts"]:
            sys_act = SysAct()
            sys_act.type = SysActionType.Bye
        # if user only says thanks, ask if they want anything else
        elif UserActionType.Thanks in beliefstate["user_acts"]:
            self.random = False
            sys_act = SysAct()
            sys_act.type = SysActionType.RequestMore
        # If user only says hello, request a random slot to move dialog along
        elif UserActionType.Hello in beliefstate["user_acts"] or UserActionType.SelectDomain in beliefstate["user_acts"]:
            sys_act = SysAct()
            sys_act.type = SysActionType.Request
            slot = self._get_open_slot(beliefstate)
            sys_act.add_value(slot)

            # If we switch to the domain, start a new dialog
            if UserActionType.SelectDomain in beliefstate["user_acts"]:
                self.dialog_start()
            self.first_turn = False

        # handle domain specific actions
        else:
            sys_act = self._next_action(beliefstate)

        self.logger.dialog_turn("System Action: " + str(sys_act))

        return {'sys_act': sys_act}


    def _query_db(self, beliefstate: BeliefState, random = False):
        """Based on the constraints specified, uses self.domain to generate the appropriate type
           of query for the database

        Returns:
            iterable: representing the results of the database lookup

        --LV
        """
        # determine if an entity has already been suggested or was mentioned by the user
        name = self._get_name(beliefstate)
        # if yes and the user is asking for info about a specific entity, generate a query to get
        # that info for the slots they have specified
        if name and beliefstate['requests']:
            requested_slots = beliefstate['requests']
            return self.domain.find_info_about_entity(name, requested_slots)
        # otherwise, issue a query to find all entities which satisfy the constraints the user
        # has given so far
        else:
            constraints, _ = self._get_constraints(beliefstate)
            return self.domain.find_entities(constraints)


    def _next_action(self, beliefstate: BeliefState):
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
        # Assuming this happens only because domain is not actually active --LV
        """if UserActionType.Bad in beliefstate['user_acts'] or beliefstate['requests'] \
                and not self._get_name(beliefstate):
            sys_act = SysAct()
            sys_act.type = SysActionType.Bad
            return sys_act, {'last_action': sys_act}"""

        if not self.has_enough_info_to_suggest(beliefstate):
            sys_act = SysAct()
            sys_act.type = SysActionType.Request
            sys_act.add_value(self._get_open_mandatory_slot(beliefstate), None)
            return sys_act

        elif UserActionType.RequestAlternatives in beliefstate['user_acts'] \
                and not self._get_constraints(beliefstate)[0]:
            sys_act = SysAct()
            sys_act.type = SysActionType.Bad
            return sys_act

        elif self.domain.get_primary_key() in beliefstate['informs'] \
                and not beliefstate['requests']:
            sys_act = SysAct()
            sys_act.type = SysActionType.InformByName
            sys_act.add_value(self.domain.get_primary_key(), self._get_name(beliefstate))
            return sys_act
        
        # Otherwise we need to query the db to determine next action
        if UserActionType.RequestRandom in beliefstate['user_acts'] :
            self.random = True
            results = self._query_db(beliefstate)
            #results = self._query_db(beliefstate, True)
            #results = [choice(self.domain.last_results[:beliefstate['num_matches']*(-1)])]
            sys_act = SysAct()
            sys_act.type = SysActionType.InformByName
        else:
            results = self._query_db(beliefstate)
            sys_act = self._raw_action(results, beliefstate)

        
        # otherwise we need to convert a raw inform into a one with proper slots and values
        if sys_act.type == SysActionType.InformByName:
            self._convert_inform(results, sys_act, beliefstate)
            # update belief state to reflect the offer we just made
            values = sys_act.get_values(self.domain.get_primary_key())
            if not values:
                sys_act.add_value(self.domain.get_primary_key(), 'none')
        elif sys_act.type == SysActionType.ShowRandom:
            #results = [choice(results)]
            self._convert_inform(results, sys_act, beliefstate)
            values = sys_act.get_values(self.domain.get_primary_key())
            if not values:
                sys_act.add_value(self.domain.get_primary_key(), 'none')

        return sys_act

    # This belongs to the case when multiple instances are returned by api
    # TODO: put this to a separate file?
    def _raw_action(self, q_res: iter, beliefstate: BeliefState) -> SysAct:
        """Based on the output of the db query and the method, choose
           whether next action should be request or inform

        Args:
            q_res (list): rows (list of dicts) returned by the issued
            query to db
           
        Returns:
            (SysAct): SysAct object of appropriate type

        --LV
        """
        sys_act = SysAct()
        # if there is more than one result
        if len(q_res) > 1:
            constraints, dontcare = self._get_constraints(beliefstate)
            # Gather all the results for each column
            temp = {key: [] for key in q_res[0].keys()}
            # If any column has multiple values, ask for clarification
            for result in q_res:
                for key in result.keys():
                    if key != self.domain.get_primary_key():
                        temp[key].append(result[key])
            next_req = self._find_possible_requests(temp, beliefstate)
           #next_req = self._get_open_slot(beliefstate)
            if next_req and not self.random:
                sys_act.type = SysActionType.SuggestRequest
                for slot in next_req:
                    sys_act.add_value(slot, None)
                return sys_act
            else:
                sys_act.type = SysActionType.ShowRandom
                return sys_act

        # Otherwise action type will be inform, so return an empty inform (to be filled in later)
        sys_act.type = SysActionType.InformByName
        return sys_act

    def _find_possible_requests(self, temp: Dict[str, List[str]], belief_state: BeliefState):
        """
        When several results are returned, either ask for more speficity or ask if a random movie should be returned
        """
        informed = [slot for slot in belief_state['informs']]
        system_requestable = self.domain.get_system_requestable_slots()
        unidentified = set(system_requestable) - set(informed)
        if unidentified:
            return unidentified
        else:
            return None

    def _convert_inform(self, q_results: iter,
                        sys_act: SysAct, beliefstate: BeliefState):
        """Fills in the slots and values for a raw inform so it can be returned as the
           next system action.

        Args:
            method (str): the type of user action
                     ('byprimarykey', 'byconstraints', 'byalternatives')
            q_results (list): Results of SQL database query
            sys_act (SysAct): the act to be modified
            belief_state(dict): contains info on what columns were queried

        --LV
        """
        if beliefstate['requests']:
            self._convert_inform_by_primkey(q_results, sys_act, beliefstate)

        elif UserActionType.RequestAlternatives in beliefstate['user_acts']:
            self._convert_inform_by_alternatives(sys_act, q_results, beliefstate)

        else:
            self._convert_inform_by_constraints(q_results, sys_act, beliefstate)

    def _convert_inform_by_primkey(self, q_results: iter,
                                   sys_act: SysAct, belief_state: BeliefState):
        """
            Helper function that adds the values for slots to a SysAct object when the system
            is answering a request for information about an entity from the user

            Args:
                q_results (iterable): list of query results from the database
                sys_act (SysAct): current raw sys_act to be filled in
                belief_state (BeliefState)

        """
        sys_act.type = SysActionType.InformByName
        if q_results:
            result = q_results[0]  # currently return just the first result
            keys_r = list(result.keys())  # should represent all user specified constraints
            requests = list(belief_state['requests'].keys())

            keys = set.intersection(set(keys_r), set(requests))

            # add slots + values (where available) to the sys_act
            for k in keys:
                res = result[k] if result[k] else 'not available'
                sys_act.add_value(k, res)
            # Name might not be a constraint in request queries, so add it
            if self.domain.get_primary_key() not in keys:
                name = self._get_name(belief_state)
                sys_act.add_value(self.domain.get_primary_key(), name)
            # Add default Inform slots
            #for slot in self.domain.get_default_inform_slots():
                #if slot not in sys_act.slot_values:
                    #sys_act.add_value(slot, result[slot])
        else:
            sys_act.add_value(self.domain.get_primary_key(), 'none')


    def _convert_inform_by_constraints(self, q_results: iter,
                                       sys_act: SysAct, belief_state: BeliefState):
        """
            Helper function for filling in slots and values of a raw inform act when the system is
            ready to make the user an offer

            Args:
                q_results (iter): the results from the databse query
                sys_act (SysAct): the raw infor act to be filled in
                belief_state (BeliefState): the current system beliefs

        """
        if list(q_results):
            self.current_suggestions = []
            self.s_index = 0
            for result in q_results:
                self.current_suggestions.append(result)
            result = self.current_suggestions[0]
            sys_act.add_value(self.domain.get_primary_key(), result[self.domain.get_primary_key()])
            # Add default Inform slots
            for slot in self.domain.get_default_inform_slots():
                if slot not in sys_act.slot_values:
                    sys_act.add_value(slot, result[slot])
        else:
            sys_act.add_value(self.domain.get_primary_key(), 'none')

        #sys_act.type = SysActionType.InformByName
        constraints, dontcare = self._get_constraints(belief_state)
        for c in constraints:
            # Using constraints here rather than results to deal with empty
            # results sets (eg. user requests something impossible) --LV
            sys_act.add_value(c, constraints[c])

        if self.current_suggestions:
            for slot in belief_state['requests']:
                if slot not in sys_act.slot_values:
                    sys_act.add_value(slot, self.current_suggestions[0][slot])
    
    def _convert_inform_by_alternatives(
            self, sys_act: SysAct, q_res: iter, belief_state: BeliefState):
        """
            Helper Function, scrolls through the list of alternative entities which match the
            user's specified constraints and uses the next item in the list to fill in the raw
            inform act.

            When the end of the list is reached, currently continues to give last item in the list
            as a suggestion

            Args:
                sys_act (SysAct): the raw inform to be filled in
                belief_state (BeliefState): current system belief state ()

        """
        if q_res and not self.current_suggestions:
            self.current_suggestions = []
            self.s_index = -1
            for result in q_res:
                self.current_suggestions.append(result)
        
        self.s_index += 1
        # here we should scroll through possible offers presenting one each turn the user asks
        # for alternatives
        if self.s_index <= len(self.current_suggestions) - 1:
            # the first time we inform, we should inform by name, so we use the right template
            if self.s_index == 0:
                sys_act.type = SysActionType.InformByName
            else:
                sys_act.type = SysActionType.InformByAlternatives
            result = self.current_suggestions[self.s_index]
            # Inform by alternatives according to our current templates is
            # just a normal inform apparently --LV
            sys_act.add_value(self.domain_key, result[self.domain_key])
        else:
            sys_act.type = SysActionType.InformByAlternatives
            # default to last suggestion in the list
            self.s_index = len(self.current_suggestions) - 1
            sys_act.add_value(self.domain.get_primary_key(), 'none')

        # in addition to the name, add the constraints the user has specified, so they know the
        # offer is relevant to them
        # Add default Inform slots
        for slot in self.domain.get_default_inform_slots():
            if slot not in sys_act.slot_values:
                sys_act.add_value(slot, result[slot])

        constraints, dontcare = self._get_constraints(belief_state)
        for c in constraints:
            sys_act.add_value(c, constraints[c])
        
    
    def has_enough_info_to_suggest(self, belief_state: BeliefState):
        """whether or not all mandatory slots have a value

        Arguments:
        """
        filled_slots, _ = self._get_constraints(belief_state)
        return self.domain.has_enough_constraints_to_query(filled_slots)
