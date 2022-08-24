############################################################################################
#
# Copyright 2020, University of Stuttgart: Institute for Natural Language Processing (IMS)
#
# This file is part of Adviser.
# Adviser is free software: you can redistribute it and/or modify'
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3.
#
# Adviser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adviser.  If not, see <https://www.gnu.org/licenses/>.
#
############################################################################################

import re, json, os
from typing import List
from utils.sysact import SysAct, SysActionType

from utils import UserAct, UserActionType, DiasysLogger
from services.service import Service, PublishSubscribe
from .actor_name_extractor import ActorNameExtractor
from . import genre_synonyms
# simple list of regexes

MOVIE_GENRE_REGEXES = [
    re.compile(r'\b(' + r')\b|\b('.join(genre_synonyms.LIST) + r')\b')
]

ACTOR_NAME_PLACEHOLDER = 'actor_placeholder'

ACTOR_NAME_REGEXES = [
    re.compile(ACTOR_NAME_PLACEHOLDER)
]

YEAR_REGEX_1 = r'((?:19[0-9]|20(?:0|1|2))\d)' # Matches any year 1900 - 2029
YEAR_REGEX_2 = r'(?:from|in|released) ([1-9]\d)' # or a more specific mention of a year by two numbers (such as '...released *in 95*...')
MOVIE_RELEASE_DATE_REGEXES = [
    re.compile(r'\b' + YEAR_REGEX_1 + r'\b'),   
    re.compile(r'\b' + YEAR_REGEX_2 + r'\b')
]

DECADE_REGEX = r"(?:from |in |released )?(?:the )?([1-9]0)'?s" # Matches a decade (the 90s, 80's etc)
MOVIE_RELEASE_DECADE_REGEXES = [
    re.compile(r'\b' + DECADE_REGEX + r'\b'),   
]

MOVIE_RELEASE_DATE_BEFORE_REGEXES = [
    re.compile(r"\b(before|older than|earlier than) " + regex) for regex in [YEAR_REGEX_1, YEAR_REGEX_2, DECADE_REGEX]
]

MOVIE_RELEASE_DATE_AFTER_REGEXES = [
    re.compile(r"\b(after|later than) " + regex) for regex in [YEAR_REGEX_1, YEAR_REGEX_2, DECADE_REGEX]
]

MOVIE_RELEASE_DATE_OLD_REGEXES = [
    re.compile(r"\b(old|classic)\b")
]

MOVIE_RELEASE_DATE_RECENT_REGEXES = [
    re.compile(r"\b(recent|latest)\b")
]

MOVIE_RELEASE_DATE_RANGE_REGEXES = [
    re.compile(r"\b(?:between|from|starting) " + YEAR_REGEX_1 + r"(?: to | ?- ?| and )" + YEAR_REGEX_1)
]

MOVIE_CAST_REQUEST_REGEX = [re.compile(r'\b((?:(?:what|which) (?:is the cast of|actors are (?:starring )?in)|who (is (?:starring |taking part |playing )?in|are the (?:actors|cast) (?:in|of))) the movie|whom? does the movie star)\b')] #TODO: improve this regex.

MOVIE_RATING_REQUEST_REGEX = [re.compile(r'\b(rating|score|is it (?:a )?(?:good|bad|ok)|how (?:good|bad|ok) is it)\b')]

#TODO: ability to request the overview: Tell me about the movie? What is it about? etc. Together with this, would be nice to not always return the rating and overview, so theres a point for the user to ask specific stuff.

SHOW_RECOMMENDATION = [
    re.compile(r'\b(recommend|recommendation|suggest|suggestion)\b')
]

FIRST_REGEXES = [
    re.compile(r'\b(first|1st|1|^one$)\b'),
]

SECOND_REGEX = [
    re.compile(r'\b(second|2nd|2|two)\b'),
]

THIRD_REGEX = [
    re.compile(r'\b(third|3rd|3|three)\b'),
]

LAST_REGEX = [
    re.compile(r'\b(last)\b'),
]

HELP_REGEX = [
    re.compile(r"\b(help|don'?t know|do not know|what can (i|you) do)\b"),
]

class MovieNLU(Service):
    """Very simple NLU for the movie domain."""

    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        self.actor_name_extractor = ActorNameExtractor(ACTOR_NAME_PLACEHOLDER)
        super(MovieNLU, self).__init__(domain, debug_logger=logger)
        #path = os.path.join('adviser', 'resources', 'nlu_regexes', 'GeneralRules.json')
        path = os.path.join('resources', 'nlu_regexes', 'GeneralRules.json')
        self.general_regex = json.load(open(path))
        self.last_sys_act = None

    @PublishSubscribe(sub_topics=["sys_act"])
    def save_last_sys_act(self, sys_act: SysAct = None):
        self.last_sys_act = sys_act

    @PublishSubscribe(sub_topics=["user_utterance"], pub_topics=["user_acts"])
    def extract_user_acts(self, user_utterance: str = None, sys_act: SysAct = None) -> dict(user_acts=List[UserAct]):
        """Main function for detecting and publishing user acts.

        Args:
            user_utterance: the user input string

        Returns:
            dict with key 'user_acts' and list of user acts as value
        """
        user_acts = []
        if not user_utterance:
            return {'user_acts': None}

        user_utterance, actors = self.actor_name_extractor(user_utterance)

        user_utterance = ' '.join(user_utterance.lower().split())

        if self.last_sys_act is not None and self.last_sys_act.type == SysActionType.InformByAlternatives:
            movie_id = self._extract_selection(user_utterance, self.last_sys_act)
            if movie_id is not None:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'id', movie_id))

        for act in self.general_regex:
            if act == 'req_everything':
                continue
            
            if re.search(self.general_regex[act], user_utterance, re.I):
                user_act_type = UserActionType(act)
                user_acts.append(UserAct(user_utterance, user_act_type))
        
        for regex in ACTOR_NAME_REGEXES:
            matches = re.finditer(regex, user_utterance)
            actor_index = 0
            for match in matches:
                try:
                    user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'cast', actors[actor_index]))
                    actor_index += 1
                except:
                    break

        for regex in MOVIE_CAST_REQUEST_REGEX:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Request, 'cast'))
        
        for regex in SHOW_RECOMMENDATION:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'looking_for_specific_movie', False))
                
        for regex in MOVIE_RATING_REQUEST_REGEX:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Request, 'rating'))

        for regex in MOVIE_GENRE_REGEXES:
            matches = list(re.finditer(regex, user_utterance))
            for match in matches:
                genre = match.group(0)
                normalized_genre = genre_synonyms.MAPPING[genre]
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'genres', normalized_genre))

        year_user_acts = self._match_years(user_utterance)
        for act in year_user_acts:
            user_acts.append(act)

        # if no helpful user act was matched, check if user needs help
        if len(user_acts) == 0:
            for regex in HELP_REGEX:
                match = regex.search(user_utterance)
                if match:
                    user_acts.append(UserAct(user_utterance, UserActionType.Help))

        # if still no user act was matched, assume it's bad input
        if len(user_acts) == 0:
            user_acts.append(UserAct(user_utterance, UserActionType.Bad)) 

        self.debug_logger.dialog_turn("User Actions: %s" % str(user_acts))

        return {'user_acts': user_acts}

    def _match_years(self, user_utterance):
        user_acts = []
        before = False
        after = False
        old = False
        recent = False
        years = []
        decades = []

        for regex in MOVIE_RELEASE_DATE_BEFORE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                before = True
                break
        for regex in MOVIE_RELEASE_DATE_AFTER_REGEXES:
            match = regex.search(user_utterance)
            if match:
                after = True
                break
       
        for regex in MOVIE_RELEASE_DATE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                year = match.group(1)
                if len(year) == 2:
                    year = '19' + year
                years.append(year)

        for regex in MOVIE_RELEASE_DECADE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                decade = match.group(1)
                decades.append(decade)

        for regex in MOVIE_RELEASE_DATE_OLD_REGEXES:
            match = regex.search(user_utterance)
            if match:
                old = True
                break

        for regex in MOVIE_RELEASE_DATE_RECENT_REGEXES:
            match = regex.search(user_utterance)
            if match:
                recent = True
                break

        for regex in MOVIE_RELEASE_DATE_RANGE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                start_year = match.group(1)
                end_year = match.group(2)
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '>=' + start_year))
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '<=' + end_year))
                return user_acts

        if len(years) > 0:
            for year in years:
                if before:
                    year = str(int(year) - 1)
                    user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '<=' + year))
                if after:
                    year = str(int(year) + 1)
                    user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '>=' + year))
                else:
                    user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', year))
        elif len(decades) == 1:
            decade = decades[0]
            start_year = '19' + decade[0] + '0'
            end_year = '19' + decade[0] + '9'
            if before:
                start_year = str(int(start_year) - 1)
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '<=' + start_year))
            elif after:
                end_year = str(int(end_year) + 1)
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '>=' + end_year))
            else:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '>=' + start_year))
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '<=' + end_year))
        elif old:
            user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '<=1980'))
        elif recent:
            user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', '>=2021'))



        return user_acts


    def _extract_selection(self, user_utterance: str, sys_act: SysAct) -> int:
        titles = [title.lower() for title in sys_act.slot_values['title']]
        movie_ids = sys_act.slot_values['id']
        i = 0
        for title in titles:
            if title in user_utterance:
                return movie_ids[i]
            i += 1
        for regex in FIRST_REGEXES:
            match = regex.search(user_utterance)
            if match:
                return movie_ids[0]
        for regex in SECOND_REGEX:
            match = regex.search(user_utterance)
            if match:
                return movie_ids[1]
        for regex in THIRD_REGEX:
            match = regex.search(user_utterance)
            if match:
                return movie_ids[2]
        for regex in LAST_REGEX:
            match = regex.search(user_utterance)
            if match:
                return movie_ids[-1]
        i = 0
        for title in titles:
            if user_utterance in title:
                return movie_ids[i]
            i += 1
        return None   
