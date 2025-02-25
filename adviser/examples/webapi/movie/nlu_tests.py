from examples.webapi.movie.test_utils import SysActFactory
from utils.sysact import SysActionType
from utils import UserAct, UserActionType

def get_nlu_tests():
    return get_basic_tests() + get_actor_tests() + get_year_tests() + get_rating_tests() + get_genre_tests() + get_recommendation_tests() + get_bad_tests()

def get_basic_tests():
    return [
        {
            'input': 'bye!', 
            'expected_output': [ UserAct("", UserActionType.Bye) ]
        },
        {
            'input': 'yep', 
            'expected_output': [ UserAct("", UserActionType.Affirm) ]
        },
        {
            'input': 'yes!', 
            'expected_output': [ UserAct("", UserActionType.Affirm) ]
        },
        {
            'input': 'nope!', 
            'expected_output': [ UserAct("", UserActionType.Deny) ]
        }
    ]

def get_actor_tests():
    return [
        {
            'input': 'I want to watch a movie with Tom Cruise', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'cast', "Tom Cruise") ]
        }
    ]

def get_genre_tests():
    return [
        {
            'input': 'I want a historical movie.', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "history") ]
        },
        {
            'input': 'I want to watch a scary movie.', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "horror") ]
        },
        {
            'input': 'Recommend me an animated movie from 2020.', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'looking_for_specific_movie', False),
                                UserAct("", UserActionType.Inform, 'genres', "animation"),
                                UserAct("", UserActionType.Inform, 'release_year', "2020")  ]
        }
    ]

def get_year_tests():
    return [
        {
            'input': 'Give me an action movie in 2020', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "action"), 
                                UserAct("", UserActionType.Inform, 'release_year', "2020")  ]
        },
        {
            'input': 'Give me a comedy released in 1998', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'release_year', "1998")  ]
        },
        {
            'input': "What's that movie with Christopher Lloyd from 85?", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'cast', "Christopher Lloyd"), 
                                UserAct("", UserActionType.Inform, 'release_year', "1985")  ]
        },
        {
            'input': "Give me a comedy from the 90s", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'release_year', '>=1990'),
                                UserAct("", UserActionType.Inform, 'release_year', '<=1999')
                                ]
        },
        {
            'input': "Give me a recent comedy movie", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'release_year', '>=2021')
                                ]
        },
        {
            'input': "Give me a classic western", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "western"), 
                                UserAct("", UserActionType.Inform, 'release_year', '<=1980')
                                ]
        },
        {
            'input': "Give me a comedy from before the 90s", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'release_year', '<=1989')
                                ]
        },
        {
            'input': "Give me a comedy movie released between 1981 and 1985", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'release_year', '>=1981'),
                                UserAct("", UserActionType.Inform, 'release_year', '<=1985')
                                ]
        },
        {
            'input': "Give me a movie released from 1970 to 1980", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'release_year', '>=1970'),
                                UserAct("", UserActionType.Inform, 'release_year', '<=1980')
                                ]
        },
        {
            'input': "Give me a movie from 1970-1980", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'release_year', '>=1970'),
                                UserAct("", UserActionType.Inform, 'release_year', '<=1980')
                                ]
        },
        {
            'input': "Give me a movie released later than 2000", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'release_year', '>=2001') ]
        },
        {
            'input': "give me one released after 1995", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'release_year', '>=1996') ]
        },
        
    ]

def get_rating_tests():
    return [
        {
            'input': "What's the rating?", 
            'expected_output': [ UserAct("", UserActionType.Request, 'rating') ]
        },
        {
            'input': "What is its score?", 
            'expected_output': [ UserAct("", UserActionType.Request, 'rating') ]
        },
        {
            'input': "Is it good?", 
            'expected_output': [ UserAct("", UserActionType.Request, 'rating') ]
        },
        {
            'input': "Is it a bad movie?", 
            'expected_output': [ UserAct("", UserActionType.Request, 'rating') ]
        },
        {
            'input': "How good is it?", 
            'expected_output': [ UserAct("", UserActionType.Request, 'rating') ]
        }
    ]

def _inform_by_alternatives_3_movies():
    return SysActFactory(SysActionType.InformByAlternatives) \
                            .title('Armageddon') \
                            .title('Mercury Rising') \
                            .title('The Siege') \
                            .id('95') \
                            .id('8838') \
                            .id('9882') \
                            .build()

def get_recommendation_tests():
    return [
        {
            'input': 'Hi! Recommend me an action movie from 1990', 
            'expected_output': [ UserAct("", UserActionType.Hello),
                                UserAct("", UserActionType.Inform, 'genres', "action"),
                                UserAct("", UserActionType.Inform, 'release_year', "1990"),
                                UserAct("", UserActionType.Inform, 'looking_for_specific_movie', False)]
        },

        {
            'input': ('The first one', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "95") ]
        },
        {
            'input': ('first', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "95") ]
        },
        {
            'input': ('armageddon', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "95") ]
        },

        {
            'input': ('The second one', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "8838") ]
        },
        {
            'input': ('2', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "8838") ]
        },
        {
            'input': ('mercury rising', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "8838") ]
        },


        {
            'input': ('last one', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "9882") ]
        },
        {
            'input': ('third one', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "9882") ]
        },
        {
            'input': ('siege', _inform_by_alternatives_3_movies()), 
            'expected_output': [ UserAct("", UserActionType.Inform, 'id', "9882") ]
        },
    ]        

def get_bad_tests():
    return [
        {
            'input': "adfgsdfghn",
            'expected_output': [ UserAct("", UserActionType.Bad) ]
        },
        {
            'input': "I don't know what to do",
            'expected_output': [ UserAct("", UserActionType.Help) ]
        },
        {
            'input': "Help me do something",
            'expected_output': [ UserAct("", UserActionType.Help) ]
        },
        {
            'input': "Help me find an action movie with Tom Cruise",
            'expected_output': [ UserAct("", UserActionType.Inform, 'genres', "action"),
                                UserAct("", UserActionType.Inform, 'cast', "Tom Cruise")]
        },
        {
            'input': "Give me any movie",
            'expected_output': [ UserAct("", UserActionType.Bad) ]
        },
    ]