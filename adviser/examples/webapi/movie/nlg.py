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

from utils import DiasysLogger
from utils import SysAct, SysActionType
from services.service import Service, PublishSubscribe

import locale
locale.setlocale(locale.LC_TIME, 'en_GB.UTF-8')


class MovieNLG(Service):
    """Simple NLG for the weather domain"""

    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        super(MovieNLG, self).__init__(domain, debug_logger=logger)

    @PublishSubscribe(sub_topics=["sys_act"], pub_topics=["sys_utterance"])
    def generate_system_utterance(self, sys_act: SysAct = None) -> dict(sys_utterance=str):
        """Main function for generating and publishing the system utterance

        Args:
            sys_act: the system act for which to create a natural language realisation

        Returns:
            dict with "sys_utterance" as key and the system utterance as value
        """

        if sys_act is None or sys_act.type == SysActionType.Welcome:
            return {'sys_utterance': 'Hi! What do you want to know about movies?'}

        if sys_act.type == SysActionType.Bad:
            return {'sys_utterance': 'Sorry, I could not understand you.'}
        elif sys_act.type == SysActionType.Bye:
            return {'sys_utterance': 'Thank you, good bye'}
        elif sys_act.type == SysActionType.Request:
            slot = list(sys_act.slot_values.keys())[0]
            if slot == 'primary_release_year':
                return {'sys_utterance': 'For which year are you looking for a movie?'}
            elif slot == 'with_genres':
                return {'sys_utterance': 'Which genre are you interested in?'}
            elif slot == 'with_actors':
                return {'sys_utterance': 'What actors are you interested in?'}
            else:
                # This should probably be changed
                assert False, 'Only a year and a genre can be requested'
        elif sys_act.type == SysActionType.SuggestRequest:
            features = list(sys_act.slot_values.keys())
            f_srt = ", ".join(features)
            return {'sys_utterance': f'I have found several movies fitting you query. Do you want me to show a random movie? Otherwise, you can additionally specify the following features: {f_srt}.'}
        elif sys_act.type == SysActionType.RequestMore:
            return {'sys_utterance': 'Do you want to look for another movie?'}
       # elif sys_act.type == SysActionType.InformByName:
       #     title = sys_act.slot_values['title'][0]
       #     cast =  sys_act.slot_values['credits'][0]
       #     return {'sys_utterance': f'{cast} was in movie {title}.'}
       # else:
       #     with_genres = sys_act.slot_values['with_genres'][0]
       #     primary_release_year = sys_act.slot_values['primary_release_year'][0]
       #     title = sys_act.slot_values['title'][0]
       #     overview = sys_act.slot_values['overview'][0]
       #     return {'sys_utterance': f'A {with_genres} movie released in {primary_release_year} is called {title}: {overview}.'}
        if sys_act.type == SysActionType.ShowRandom:
            str_output = self.debug_output(sys_act)
            return {'sys_utterance': "I've found several movies fitting the query, but no further selection is possible. Showing a random one:\n" + str_output}
        else:          
            #output = self.debug_output(sys_act)
            output = InformTemplates(sys_act.slot_values).generate()

            return {'sys_utterance': output}

    def debug_output(self, sys_act):
        output = dict()
        try:
            output['with_genres'] = sys_act.slot_values['with_genres'][0]
        except:
            pass
        try:
            output['primary_release_year'] = sys_act.slot_values['primary_release_year'][0]
        except:
            pass
        try:
            output['title'] = sys_act.slot_values['title'][0]
        except:
            pass
        try:
            output['cast'] = sys_act.slot_values['credits'][0]
        except:
            pass
        try:
            output['cast'] = sys_act.slot_values['credits'][0]
        except:
            pass
        try:
            output['overview'] = sys_act.slot_values['overview'][0]
        except:
            pass
        try:
            output['rating'] = sys_act.slot_values['vote_average'][0]
        except:
            pass
        str_output = ""
        for k,v in output.items():
            str_output += f'{k}:\t{v}\n'
        return str_output[:-1]


class InformTemplates(): 
    def __init__(self, slot_values):
        self.slot_values = slot_values
        
    def _pick_template(self):
        if "vote_average" in self.slot_values:
            return "The {genre} {title} {released_in} {release_year} {starring} {actors} is rated {rating}."
        elif "primary_release_year" in self.slot_values:
            return "The {genre} {title} {starring} {actors} was released in {release_year}."
        elif "with_actors" in self.slot_values:
            return "The {genre} {title} stars {actors}."
        elif "with_genres" in self.slot_values:
            return "{title} is {a_or_an_genre}."
        else:
            return "I found the movie {title}. What do you want to know about it?"

    def generate(self):
        template = self._pick_template()
        template = template.replace('{genre}', self._genre()) \
                           .replace('{a_or_an_genre}', self._a_or_an(self._genre())) \
                           .replace('{title}', self._title()) \
                           .replace('{actors}', self._actors()) \
                           .replace('{starring}', 'starring' if self._actors() else "") \
                           .replace('{release_year}', self._release_year()) \
                           .replace('{released_in}', 'released in' if self._release_year() else "") \
                           .replace('{rating}', self._rating())
        tokens = template.split(' ')
        tokens_without_empty = [x for x in tokens if x]
        text = ' '.join(tokens_without_empty)
        overview = self._get_slot_value('overview')
        if overview:
            text += f" Here's a short description: {overview[0]}"
        return text

    def _get_slot_value(self, slot):
        try:
            return self.slot_values[slot]
        except:
            return None

    def _a_or_an(self, text):
        determiner = 'an' if text[0] in "aioeu" else 'a'
        return  f"{determiner} {text}"

    def _actors(self):
        actors = self._get_slot_value('with_actors')
        if actors:
            if len(actors) == 1:
                return f"{actors[0]}" 
            else:
                return f"{', '.join(actors[:-1])} and {actors[-1]}"
        else:
            return ""

    def _genre(self):
        genres = self._get_slot_value('with_genres')
        if genres:
            return f"{' '.join(genres)} movie"
        else:
            return "movie"

    def _title(self):
        title = self._get_slot_value('title')
        if title:
            return f"{title[0]}"
        else:
            return ""

    def _release_year(self):
        release_year = self._get_slot_value('primary_release_year')
        if release_year:
            return f"{release_year[0]}"
        else:
            return ""

    def _rating(self):
        rating = self._get_slot_value('vote_average')
        if rating:
            return f"{rating[0]}"
        else:
            return ""



