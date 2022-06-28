from typing import List, Set

from services.service import PublishSubscribe
from services.service import Service
from utils.beliefstate import BeliefState
from utils.useract import UserActionType, UserAct


class MovieBST(Service):
    """
    A rule-based approach to belief state tracking.
    """

    def __init__(self, domain=None, logger=None):
        Service.__init__(self, domain=domain)
        self.logger = logger
        self.bs = BeliefState(domain)

    @PublishSubscribe(sub_topics=["user_acts"], pub_topics=["beliefstate"])
    def update_bst(self, user_acts: List[UserAct] = None) \
            -> dict(beliefstate=BeliefState):
        """
            Updates the current dialog belief state (which tracks the system's
            knowledge about what has been said in the dialog) based on the user actions generated
            from the user's utterances

            Args:
                user_acts (list): a list of UserAct objects mapped from the user's last utterance

            Returns:
                (dict): a dictionary with the key "beliefstate" and the value the updated
                        BeliefState object

        """
        # save last turn to memory
        self.bs.start_new_turn()
        if user_acts:
            thank = False
            for act in user_acts:
                if act.type == UserActionType.Thanks:
                    thank = True
            if len(user_acts)== 1 and thank:
                self._reset_all_informs()
                self.bs["user_acts"] = self._get_all_usr_action_types(user_acts)
                self._reset_requests()
                self.bs["num_matches"] = 0
                self.bs["discriminable"] = True
            else:
                self._reset_informs(user_acts)
                self._reset_requests()
                self.bs["user_acts"] = self._get_all_usr_action_types(user_acts)

                self._handle_user_acts(user_acts)

                num_entries, discriminable = self.bs.get_num_dbmatches()
                self.bs["num_matches"] = num_entries
                self.bs["discriminable"] = discriminable

        return {'beliefstate': self.bs}

    def dialog_start(self):
        """
            Restets the belief state so it is ready for a new dialog

            Returns:
                (dict): a dictionary with a single entry where the key is 'beliefstate'and
                        the value is a new BeliefState object
        """
        # initialize belief state
        self.bs = BeliefState(self.domain)

    def _reset_informs(self, acts: List[UserAct]):
        """
            If the user specifies a new value for a given slot, delete the old
            entry from the beliefstate
        """

        slots = {act.slot for act in acts if act.type == UserActionType.Inform}
        for slot in [s for s in self.bs['informs']]:
            if slot in slots:
                del self.bs['informs'][slot]
    
    def _reset_all_informs(self):
        """
            If the user specifies a new value for a given slot, delete the old
            entry from the beliefstate
        """
        for slot in [s for s in self.bs['informs']]:
                del self.bs['informs'][slot]

    def _reset_requests(self):
        """
            gets rid of requests from the previous turn
        """
        self.bs['requests'] = {}

    def _get_all_usr_action_types(self, user_acts: List[UserAct]) -> Set[UserActionType]:
        """ 
        Returns a set of all different UserActionTypes in user_acts.

        Args:
            user_acts (List[UserAct]): list of UserAct objects

        Returns:
            set of UserActionType objects
        """
        action_type_set = set()
        for act in user_acts:
            action_type_set.add(act.type)
        return action_type_set

    def _handle_user_acts(self, user_acts: List[UserAct]):

        """
            Updates the belief state based on the information contained in the user act(s)

            Args:
                user_acts (list[UserAct]): the list of user acts to use to update the belief state

        """
        
        # reset any offers if the user informs any new information
        if self.domain.get_primary_key() in self.bs['informs'] \
                and UserActionType.Inform in self.bs["user_acts"]:
            del self.bs['informs'][self.domain.get_primary_key()]

        # We choose to interpret switching as wanting to start a new dialog and do not support
        # resuming an old dialog
        elif UserActionType.SelectDomain in self.bs["user_acts"]:
            self.bs["informs"] = {}
            self.bs["requests"] = {}

        # Handle user acts
        for act in user_acts:
            if act.type == UserActionType.Request:
                self.bs['requests'][act.slot] = act.score
                #self.bs['informs'][self.domain.get_primary_key()] = {str(self.domain.last_results[-1][self.domain.get_primary_key()]):1.0}
            elif act.type == UserActionType.Inform:
                # add informs and their scores to the beliefstate
                if act.slot in self.bs["informs"]:
                    self.bs['informs'][act.slot][act.value] = act.score
                else:
                    self.bs['informs'][act.slot] = {act.value: act.score}
            elif act.type == UserActionType.NegativeInform:
                # reset mentioned value to zero probability
                if act.slot in self.bs['informs']:
                    if act.value in self.bs['informs'][act.slot]:
                        del self.bs['informs'][act.slot][act.value]
            elif act.type == UserActionType.RequestAlternatives:
                # This way it is clear that the user is no longer asking about that one item
                if self.domain.get_primary_key() in self.bs['informs']:
                    del self.bs['informs'][self.domain.get_primary_key()]
