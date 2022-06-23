from services.policy.policy_api import HandcraftedPolicy
from services.service import PublishSubscribe, Service

from utils import SysAct, SysActionType
from utils.beliefstate import BeliefState
from utils.useract import UserActionType


class MoviePolicy(HandcraftedPolicy):
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


    def _query_db(self, beliefstate: BeliefState):
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
        results = self._query_db(beliefstate)
        sys_act = self._raw_action(results, beliefstate)

        # otherwise we need to convert a raw inform into a one with proper slots and values
        if sys_act.type == SysActionType.InformByName:
            self._convert_inform(results, sys_act, beliefstate)
            # update belief state to reflect the offer we just made
            values = sys_act.get_values(self.domain.get_primary_key())
            if not values:
                sys_act.add_value(self.domain.get_primary_key(), 'none')

        return sys_act

    def _raw_action(self, q_res: iter, beliefstate: BeliefState) -> SysAct:
        """Based on the output of the db query and the method, choose
           whether next action should be request or inform

        Args:
            q_res (list): rows (list of dicts) returned by the issued sqlite3
            query
            method (str): the type of user action
                     ('byprimarykey', 'byconstraints', 'byalternatives')

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
                    if key != self.domain_key:
                        temp[key].append(result[key])
            next_req = self._gen_next_request(temp, beliefstate)
            if next_req:
                sys_act.type = SysActionType.Request
                sys_act.add_value(next_req)
                return sys_act

        # Otherwise action type will be inform, so return an empty inform (to be filled in later)
        sys_act.type = SysActionType.InformByName
        return sys_act

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
            if self.domain_key not in keys:
                name = self._get_name(belief_state)
                sys_act.add_value(self.domain_key, name)
            # Add default Inform slots
            #for slot in self.domain.get_default_inform_slots():
                #if slot not in sys_act.slot_values:
                    #sys_act.add_value(slot, result[slot])
        else:
            sys_act.add_value(self.domain_key, 'none')


    def has_enough_info_to_suggest(self, belief_state: BeliefState):
        """whether or not all mandatory slots have a value

        Arguments:
        """
        filled_slots, _ = self._get_constraints(belief_state)
        return self.domain.has_enough_constraints_to_query(filled_slots)
