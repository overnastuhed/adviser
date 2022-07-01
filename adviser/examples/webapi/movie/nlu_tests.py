from utils import UserAct, UserActionType

def get_nlu_tests():
    return get_basic_tests() + get_actor_tests() + get_year_tests() + get_rating_tests() + get_genre_tests() + get_recommendation_tests()

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
                                UserAct("", UserActionType.Inform, 'release_decade', "1990")  ]
        }
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

def get_recommendation_tests():
    return [
        {
            'input': 'Hi! Recommend me an action movie from 1990', 
            'expected_output': [ UserAct("", UserActionType.Hello),
                                UserAct("", UserActionType.Inform, 'genres', "action"),
                                UserAct("", UserActionType.Inform, 'release_year', "1990"),
                                UserAct("", UserActionType.Inform, 'looking_for_specific_movie', False)]
        }
    ]        