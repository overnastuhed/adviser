###############################################################################
#
# Copyright 2020, University of Stuttgart: Institute for Natural Language Processing (IMS)
#
# This file is part of Adviser.
# Adviser is free software: you can redistribute it and/or modify
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
###############################################################################

from typing import List, Iterable
import tmdbsimple as tmdb
from datetime import datetime
from random import choice

from utils.domain.lookupdomain import LookupDomain

API_KEY = 'EnterYourPersonalAPIKeyFromTMDB'
tmdb.API_KEY = input('TMDB API_KEY: ')

genres = tmdb.Genres().movie_list()['genres']
genre2id = dict()
id2genre = dict()
for elem in genres:
    i = elem['id']
    name = elem['name']
    genre2id[name.lower()] = i
    id2genre[i] = name.lower()


class MovieDomain(LookupDomain):
    """Domain for the Movie API.

    Attributes:
        last_results (List[dict]): Current results which the user might request info about
    """

    def __init__(self):
        LookupDomain.__init__(self, 'MovieAPI', 'Movie')

        self.last_results = []

    def find_entities(self, constraints: dict, requested_slots: Iterable = iter(())):
        """ Returns all entities from the data backend that meet the constraints.

        Args:
            constraints (dict): Slot-value mapping of constraints.
                                If empty, all entities in the database will be returned.
            requested_slots (Iterable): list of slots that should be returned in addition to the
                                        system requestable slots and the primary key
        """
        if self.has_enough_constraints_to_query(constraints):

            #TODO: Handle case when no movies are found   
            years = self._get_requested_years(constraints) 
            suggestions = self._query(constraints['with_genres'], years, constraints['with_actors'])
            suggestion = choice(suggestions)
            if suggestion is None:
                return []

            title = suggestion['original_title']
            overview = suggestion['overview']
            tmdb_id = suggestion['id']
            rating = suggestion['vote_average']
            release_year = self._get_year_from_date(suggestion['release_date'])

            result_dict = {
                'artificial_id': str(len(self.last_results)),
                'original_id' : tmdb_id,
                'title': title,
                'overview': overview,
                'primary_release_year': release_year,
                'with_genres': constraints['with_genres'],
                'with_actors': constraints['with_actors'],
                'rating':rating
            }

            if any(True for _ in requested_slots):
                cleaned_result_dict = {slot: result_dict[slot] for slot in requested_slots}
            else:
                cleaned_result_dict = result_dict
            #self.last_results.append(cleaned_result_dict)
            self.last_results.append(result_dict)
            return [cleaned_result_dict]
        else:
            return []

    def find_info_about_entity(self, entity_id, requested_slots: Iterable):
        """ Returns the values (stored in the data backend) of the specified slots for the
            specified entity.

        Args:
            entity_id (str): primary key value of the entity
            requested_slots (dict): slot-value mapping of constraints
        """
        tmdb_id = self.last_results[int(entity_id)]['original_id']
        output = self.last_results[int(entity_id)]
        if 'credits' in requested_slots:
            full_cast = tmdb.Movies(id=tmdb_id).credits()['cast']
            #for i in range(1):
                #some_cast.append(cast[i]['name'])
            some_cast = full_cast[1]['name']
        #return [{'credits':some_cast}]
            output['credits'] = some_cast
        #print(output)
        return [output]

    def get_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the user. What the system tells the user. """
        return ['title', 'overview']

    def get_system_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the system. What the system can ask the user. """
        return ['with_genres', 'primary_release_year', 'with_actors']

    def get_informable_slots(self) -> List[str]:
        """ Returns a list of all informable slots. What user tells the system."""
        return ['with_genres', 'primary_release_year', 'release_decade', 'with_actors']

    def get_mandatory_slots(self) -> List[str]:
        """ Returns a list of all mandatory slots. """
        return ['with_genres', 'primary_release_year', 'with_actors']
        
    def get_default_inform_slots(self) -> List[str]:
        """ Returns a list of all default Inform slots. """
        return ['title', 'overview']

    def get_possible_values(self, slot: str) -> List[str]:
        """ Returns all possible values for an informable slot

        Args:
            slot (str): name of the slot

        Returns:
            a list of strings, each string representing one possible value for
            the specified slot.
         """
        raise BaseException('all slots in this domain do not have a fixed set of '
                            'values, so this method should never be called')

    def get_primary_key(self) -> str:
        """ Returns the slot name that will be used as the 'name' of an entry """
        return 'artificial_id'

    def _query(self, with_genres, primary_release_year, with_actors):
        person = tmdb.Search().person(query = with_actors)['results'][0]['id']
        output = tmdb.Discover().movie(with_genres=genre2id[with_genres], primary_release_year=primary_release_year, with_cast=[person])
        return output['results']

    def has_enough_constraints_to_query(self, constraints):
        return 'with_genres' in constraints \
            and ('primary_release_year' in constraints or 'release_decade' in constraints) \
            and 'with_actors' in constraints 

    def _get_requested_years(self, constraints):
        if 'primary_release_year' in constraints:
            return constraints['primary_release_year']
        elif 'release_decade' in constraints:
            decade = constraints['release_decade']
            return [decade[0:3] + str(n) for n in range(10)]
        
    def _get_year_from_date(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%d').year

    def get_keyword(self):
        return 'movie'
