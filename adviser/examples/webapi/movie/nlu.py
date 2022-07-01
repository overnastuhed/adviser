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

MOVIE_RELEASE_DATE_REGEXES = [
    re.compile(r'\b((?:19[0-9]|20(?:0|1|2))\d)\b'),   # Matches any year 1900 - 2029
    re.compile(r'\b(?:from|in|released) ([1-9]\d)\b') # or a more specific mention of a year by two numbers (such as '...released *in 95*...')
]

MOVIE_RELEASE_DECADE_REGEXES = [
    re.compile(r"\b(?:from|in|released) (?:the )?([1-9]0)'?s\b") # Matches a decade (the 90s, 80's etc)
]

MOVIE_CAST_REQUEST_REGEX = [re.compile(r'\b(what is the cast of the movie)\b')]

MOVIE_RATING_REQUEST_REGEX = [re.compile(r'\b(rating|score|is it (?:a )?(?:good|bad|ok)|how (?:good|bad|ok) is it)\b')]

SHOW_RECOMMENDATION = [
    re.compile(r'\b(recommend|recommendation|suggest|suggestion)\b')
]

SHOW_ANOTHER = [re.compile(r'\b(show me another one)\b')]

class MovieNLU(Service):
    """Very simple NLU for the movie domain."""

    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        self.actor_name_extractor = ActorNameExtractor(ACTOR_NAME_PLACEHOLDER)
        super(MovieNLU, self).__init__(domain, debug_logger=logger)
        path = os.path.join('adviser', 'resources', 'nlu_regexes', 'GeneralRules.json')
        self.general_regex = json.load(open(path))

    @PublishSubscribe(sub_topics=["user_utterance"], pub_topics=["user_acts"])
    def extract_user_acts(self, user_utterance: str = None) -> dict(user_acts=List[UserAct]):
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

        for act in self.general_regex:
            if re.search(self.general_regex[act], user_utterance, re.I):
                if act != 'dontcare' and act != 'req_everything':
                    user_act_type = UserActionType(act)
                    user_acts.append(UserAct(user_utterance, user_act_type))
        
        for regex in ACTOR_NAME_REGEXES:
            matches = re.finditer(regex, user_utterance)
            actor_index = 0
            for match in matches:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'cast', actors[actor_index]))
                actor_index += 1

        
        for regex in MOVIE_CAST_REQUEST_REGEX:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Request, 'cast'))
        
        for regex in SHOW_RECOMMENDATION:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.RequestRecommendation))
        
        for regex in SHOW_ANOTHER:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.RequestAlternatives))
        
        for regex in MOVIE_RATING_REQUEST_REGEX:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Request, 'rating'))

        for regex in MOVIE_GENRE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                genre = match.group(0)
                normalized_genre = genre_synonyms.MAPPING[genre]
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'genres', normalized_genre))

        for regex in MOVIE_RELEASE_DATE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                year = match.group(1)
                if len(year) == 2:
                    year = '19' + year
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_year', year))

        #TODO: Make sure this still works
        for regex in MOVIE_RELEASE_DECADE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                decade = '19' + match.group(1)
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'release_decade', decade))


        self.debug_logger.dialog_turn("User Actions: %s" % str(user_acts))

        return {'user_acts': user_acts}
