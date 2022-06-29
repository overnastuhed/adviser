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

#API_KEY = 'EnterYourPersonalAPIKeyFromTMDB'
tmdb.API_KEY = open("examples/webapi/movie/api_key.txt", "r").read()

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

    def get_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the user. What the system tells the user. """
        return ['title', 'overview']

    def get_system_requestable_slots(self) -> List[str]:
        """ Returns a list of all slots requestable by the system. What the system can ask the user.
            The system will ask in the order that they are given here
         """
        return ['genres', 'cast', 'release_year']

    def get_informable_slots(self) -> List[str]:
        """ Returns a list of all informable slots. What user tells the system."""
        #return ['with_genres', 'primary_release_year', 'release_decade', 'with_actors']
        #return ['with_genres', 'primary_release_year', 'with_actors']
        return ['primary_release_year']

    def get_mandatory_slots(self) -> List[str]:
        """ Returns a list of all mandatory slots. """
        return []
        
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

    def query(self, constraints):
        #TODO: handle multiple cast members
        if 'cast' in constraints:
            try:
                person = tmdb.Search().person(query = constraints['cast'])['results'][0]
            except Exception as e:
                print("EXCEPTION while querying for person: ", e)
                person = None
        else:
            person = None

        #TODO: make use of all genres that are passed, not just one
        genre = list(constraints['genres'].keys())[0] if 'genres' in constraints else None
        genre_id = genre2id[genre] if genre else None
        year = constraints['release_year'] if 'release_year' in constraints else None

        if person is None and genre is None and year is None:
            return []
        else:
            try:
                person_id = [person['id']] if person else None
                api_result = tmdb.Discover().movie(with_genres=genre_id, primary_release_year=year, with_cast=person_id)
                return self._canonicalize_api_result(api_result, person)
            except Exception as e:
                print("EXCEPTION while querying API: ", e)
                return []

    def _canonicalize_api_result(self, api_response, person):
        """ 
        Takes the fieds from the api result that we care about and renames them
        to make them consistent across the code. 
        
        Past this point, we don't care about what the api calls different fields.
        """
        results = api_response['results']
        canonicalized_results = []
        for movie in results:
            canonicalized_movie = {}
            if 'id' in movie:
                canonicalized_movie['id'] = str(movie['id'])
            if 'title' in movie:
                canonicalized_movie['title'] = movie['original_title']
            if 'overview' in movie:
                canonicalized_movie['overview'] = movie['overview']
            if 'release_date' in movie:
                canonicalized_movie['release_year'] = movie['release_date'][:4]
            if 'genre_ids' in movie:
                canonicalized_movie['genres'] = [id2genre[genre_id] for genre_id in movie['genre_ids']]
            if person is not None and 'name' in person:
                canonicalized_movie['cast'] = person['name']
            if 'vote_average' in movie:
                canonicalized_movie['rating'] = str(movie['vote_average'])
            canonicalized_results.append(canonicalized_movie)
        return canonicalized_results

    def get_keyword(self):
        return 'movie'
