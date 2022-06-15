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

import re, time
from datetime import datetime, timedelta
from typing import List

from utils import UserAct, UserActionType, DiasysLogger, SysAct, BeliefState
from services.service import Service, PublishSubscribe
# simple list of regexes

MOVIE_GENRE_REGEXES = [
    re.compile(r'\b(action)\b|\b(adventure)\b|\b(animation)\b|\b(comedy)\b|\b(crime)\b|\b(documentary)\b|\b(drama)\b|\b(family)\b|\b(fantasy)\b|\b(history)\b|\b(horror)\b|\b(music)\b|\b(mystery)\b|\b(romance)\b|\b(science fiction)\b|\b(tv movie)\b|\b(thriller)\b|\b(war)\b|\b(western)\b')
]

ACTOR_NAME_REGEXES = [
    re.compile(r'actor_placeholder')
]


MOVIE_RELEASE_DATE_REGEXES = [
    re.compile(r'\bin (year )?(\d{4})\b')
]

class ActorNameExtractor:
    """Very simple NLU for the movie domain."""

    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        from transformers import pipeline

        tokenizer = AutoTokenizer.from_pretrained("elastic/distilbert-base-uncased-finetuned-conll03-english")
        model = AutoModelForTokenClassification.from_pretrained("elastic/distilbert-base-uncased-finetuned-conll03-english")

        self.ner = pipeline("ner", model=model, tokenizer=tokenizer)

    def __call__(self, text):
        start = time.time()

        print(self.ner)
        print(text)
        results = self.ner(text)

        end = time.time()
        print(end - start)
        print(results)

        actors = []
        current_entity_start = None
        current_entity_end = None
        for result in results:
            if result["entity"] == "B-PER":
                start = result["start"]
                end = result["end"]
                if current_entity_start is not None and current_entity_start != start:
                    actors.append(text[current_entity_start:current_entity_end])

                current_entity_start = start
                current_entity_end = end
            elif result["entity"] == "I-PER":
                current_entity_end = result["end"]
            else:
                if current_entity_start is not None:
                    actors.append(text[current_entity_start:current_entity_end])
                    current_entity_start = None
                    current_entity_end = None

        if current_entity_start is not None:
            actors.append(text[current_entity_start:current_entity_end])

        for actor in actors:
            text = text.replace(actor, "ACTOR_PLACEHOLDER")

        return text, actors


class MovieNLU(Service):
    """Very simple NLU for the movie domain."""

    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        self.actor_name_extractor = ActorNameExtractor()
        super(MovieNLU, self).__init__(domain, debug_logger=logger)

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
        print ({'actors': actors })
        print(user_utterance)

        user_utterance = ' '.join(user_utterance.lower().split())

        for bye in ('bye', 'goodbye', 'byebye', 'seeyou'):
            if user_utterance.replace(' ', '').endswith(bye):
                return {'user_acts': [UserAct(user_utterance, UserActionType.Bye)]}
        
        print(user_utterance)
        for regex in ACTOR_NAME_REGEXES:
            matches = re.finditer(regex, user_utterance)
            actor_index = 0
            for match in matches:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'with_actors', actors[actor_index]))
                print(actors[actor_index])
                actor_index += 1

        for regex in MOVIE_GENRE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'with_genres', match.group(0)))
        for regex in MOVIE_RELEASE_DATE_REGEXES:
            match = regex.search(user_utterance)
            if match:
                user_acts.append(UserAct(user_utterance, UserActionType.Inform, 'primary_release_year', match.group(2)))

        self.debug_logger.dialog_turn("User Actions: %s" % str(user_acts))
        #print(user_acts)
        return {'user_acts': user_acts}
