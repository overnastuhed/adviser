from utils import UserAct, UserActionType

def get_nlu_tests():
    return [
        {
            'input': 'I want to watch a movie with Tom Cruise', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_actors', "Tom Cruise") ]
        },
        {
            'input': 'Suggest me an action movie in 2020', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_genres', "action"), 
                                UserAct("", UserActionType.Inform, 'primary_release_year', "2020")  ]
        },
        {
            'input': 'Suggest me a comedy from 2020', 
            'expected_output': [ UserAct("", UserActionType.Inform, 'with_genres', "comedy"), 
                                UserAct("", UserActionType.Inform, 'primary_release_year', "2020")  ]
        }
    ]