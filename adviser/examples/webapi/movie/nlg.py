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
            return {'sys_utterance': 'Hi! Lets talk about movies. What kind of movie are you looking for? You can tell me the following: genre, cast, and release year.'}

        if sys_act.type == SysActionType.Bad:
            return {'sys_utterance': 'Sorry, I could not understand you.'}
        elif sys_act.type == SysActionType.Bye:
            return {'sys_utterance': 'Thank you, good bye!'}
        elif sys_act.type == SysActionType.Help:
            return {'sys_utterance': 'I can help you find a movie based on its genre, cast, and release year.'}
        elif sys_act.type == SysActionType.Request:
            slot = list(sys_act.slot_values.keys())[0]
            if slot == 'release_year':
                return {'sys_utterance': 'Multiple movies found. To narrow down the search, could you please tell me for which year you are looking for a movie?'}
            elif slot == 'genres':
                return {'sys_utterance': 'Multiple movies found. To narrow down the search, could you please tell me which genre you are interested in?'}
            elif slot == 'cast':
                return {'sys_utterance': 'Multiple movies found. To narrow down the search, could you please tell me what actors you are interested in?'}
            else:
                # This should probably be changed
                assert False, 'Only a year and a genre can be requested'
        elif sys_act.type == SysActionType.SuggestRequest: #TODO: this action isn't used in the policy currently... Maybe it could also be changed to a regular Request (requesting 'looking_for_specific_movie')?
            features = list(sys_act.slot_values.keys())
            f_srt = ", ".join(features)
            return {'sys_utterance': f'I have found several movies fitting you query. Do you want me to show a random movie? Otherwise, you can additionally specify the following features: {f_srt}.'}
        elif sys_act.type == SysActionType.RequestMore:
            return {'sys_utterance': 'Do you want to look for another movie?'}
        elif sys_act.type == SysActionType.ShowRecommendation:
            output = InformTemplates(sys_act.slot_values).generate()
            return {'sys_utterance': "How about this one?\n" + output}
        elif sys_act.type == SysActionType.InformByAlternatives:
            counter = 1
            movie_titles = ""
            for title in sys_act.slot_values['title']:
                movie_titles += "\n" + f"{counter}) '{title}'" 
                counter += 1

            if 'num_results' in sys_act.slot_values:
                num_results = sys_act.slot_values['num_results'][0]
                message = f"I've found {num_results} movies. The 3 most popular ones are: {movie_titles}\nWhich one do you want to know more about?"

            else:
                message = f"I've found {counter-1} movies. Which one do you want to know more about? {movie_titles}"

            return {'sys_utterance': message}
        elif sys_act.type == SysActionType.NothingFound:
            return {'sys_utterance': 'I could not find any movies fitting your query.'}
        elif sys_act.type == SysActionType.InformByName:          
            #output = self.debug_output(sys_act)
            output = InformTemplates(sys_act.slot_values).generate()
            return {'sys_utterance': output}
        elif sys_act.type == SysActionType.Confirm:
            if 'confirm' not in sys_act.slot_values:
                output = "Are you sure?"
            else:
                if sys_act.slot_values['confirm'] == ['looking_for_specific_movie']:
                    if 'genres' in sys_act.slot_values:
                        genres = ' '.join(sys_act.slot_values['genres'])
                        output = f"Are you looking for a specific {genres} movie?"
                    else:
                        output = "Are you looking for a specific movie?"
                else:
                    output = "MISSING TEMPLATE FOR CONFIRM! Passed slot values: " + ' '.join(list(sys_act.slot_values.keys()))
            return {'sys_utterance': output}

        else:
            raise NotImplementedError(f'NLG for {sys_act.type} not implemented')

    def debug_output(self, sys_act):
        output = dict()
        try:
            output['genres'] = sys_act.slot_values['genres'][0]
        except:
            pass
        try:
            output['release_year'] = sys_act.slot_values['release_year'][0]
        except:
            pass
        try:
            output['title'] = sys_act.slot_values['title'][0]
        except:
            pass
        try:
            output['cast'] = sys_act.slot_values['cast'][0]
        except:
            pass
        try:
            output['overview'] = sys_act.slot_values['overview'][0]
        except:
            pass
        try:
            output['rating'] = sys_act.slot_values['rating'][0]
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
        if "rating" in self.slot_values:
            return "The {genre} {title} {released_in} {release_year} {starring} {actors} is rated {rating}."
        elif "release_year" in self.slot_values:
            return "The {genre} {title} {starring} {actors} was released in {release_year}."
        elif "cast" in self.slot_values:
            return "The {genre} {title} stars {actors}."
        elif "genres" in self.slot_values:
            return "{title} is {a_or_an_genre}."
        elif "title" in self.slot_values:
            return "I found the movie {title}. What do you want to know about it?"
        else:
            return "MISSING TEMPLATE FOR INFORM! Passed slot values: " + ' '.join(list(self.slot_values.keys()))
            
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
        actors = self._get_slot_value('cast')
        if actors:
            if len(actors) == 1:
                return f"{actors[0]}" 
            else:
                return f"{', '.join(actors[:-1])} and {actors[-1]}"
        else:
            return ""

    def _genre(self):
        genres = self._get_slot_value('genres')
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
        release_year = self._get_slot_value('release_year')
        if release_year:
            return f"{release_year[0]}"
        else:
            return ""

    def _rating(self):
        rating = self._get_slot_value('rating')
        if rating:
            return f"{rating[0]}"
        else:
            return ""



