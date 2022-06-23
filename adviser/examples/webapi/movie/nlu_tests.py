from utils import UserAct, UserActionType

def get_nlu_tests():
    return get_actor_tests() + get_year_tests()

def get_actor_tests():
    return [
        {
            'input': 'I want to watch a movie with Tom Cruise', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_actors', "Tom Cruise") ]
        }
    ]

def get_year_tests():
    return [
        {
            'input': 'Suggest me an action movie in 2020', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_genres', "action"), 
                                UserAct("", UserActionType.Inform, 'primary_release_year', "2020")  ]
        },
        {
            'input': 'Suggest me a comedy released in 1998', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'primary_release_year', "1998")  ]
        },
        {
            'input': "What's that movie with Christopher Lloyd from 85?", 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_actors', "Christopher Lloyd"), 
                                UserAct("", UserActionType.Inform, 'primary_release_year', "1985")  ]
        }
    ]