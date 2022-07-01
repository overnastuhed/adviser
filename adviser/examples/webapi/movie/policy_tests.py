from utils.sysact import SysActionType
from .test_utils import SysActFactory, BeliefStateFactory

def get_policy_tests():
    return get_general_tests() + get_question_answering_tests()

def get_general_tests():
    return [
        {
            'input': BeliefStateFactory().build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Welcome).build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .new_turn()
                        .request('rating')
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Request)
                            .genre()        
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .inform('genres', 'action')
                        .inform('cast', 'Tom Cruise')
                        .new_turn()
                        .request('rating')
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.InformByName)
                            .rating(any=True)        
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .inform('genres', 'action')
                        .inform('cast', 'Tom Cruise')                
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.InformByName)
                            .id(any=True)
                            .title('Top Gun')    
                            .overview("For Lieutenant Pete 'Maverick' Mitchell and his friend and co-pilot Nick 'Goose' Bradshaw, being accepted into an elite training school for fighter pilots is a dream come true. But a tragedy, as well as personal demons, will threaten Pete's dreams of becoming an ace pilot.")        
                            .year('1986')
                            .genre('action')
                            .genre('drama')
                            .genre('adventure')
                            .actor('Tom Cruise')
                            .rating('7')
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('genres', 'action')
                        .inform('cast', 'Tom Cruise') 
                        .inform('looking_for_specific_movie', False)
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.ShowRecommendation)
                            .id(any=True)
                            .title(any=True)    
                            .overview(any=True)        
                            .year(any=True)
                            .genre(containing=['action'])
                            .actor('Tom Cruise')
                            .rating(any=True)
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .inform('genres', 'action')
                        .inform('cast', 'Tom Cruise')   
                        .new_turn(SysActFactory(SysActionType.InformByName).id('744').build()) # 744 is Top Gun, system already suggested it once so shouldn't suggest it again
                        .request_alternative()            
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.NothingFound)
                            .build()
            }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1990')
                        .inform('genres', 'action')
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Request)
                            .actor()
                            .build()
            }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .inform('genres', 'action')
                        .new_turn()
                        .inform('cast', 'Tom Cruise')
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.InformByName)
                            .id(any=True)
                            .title(any=True)    
                            .overview(any=True)        
                            .year('1986')
                            .genre(containing=['action'])
                            .actor('Tom Cruise')
                            .rating(any=True)
                            .build()
            }
        },
        {
            'input': BeliefStateFactory()
                        .inform('release_year', '1986')
                        .inform('genres', 'action')
                        .inform('cast', 'Tom Cruise')
                        .new_turn(SysActFactory(SysActionType.InformByName).id('744').build()) # 744 is Top Gun, system already suggested it once so shouldn't suggest it again
                        .request('rating')
                        .new_turn(SysActFactory(SysActionType.InformByName).rating('7').build())
                        .bye()
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Bye)
                            .build()
            }
        }
    ]

def get_question_answering_tests():
    return [
        {
            'input': BeliefStateFactory()
                        .inform('genres', 'comedy')                         # User is asking for a comedy
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Confirm)             # System confirming that they're looking for a suggestion, not a specific movie
                            .confirm('looking_for_specific_movie')
                            .genre('comedy')    
                            .build()
            }
        },
        {
            'input': BeliefStateFactory()
                        .inform('genres', 'comedy')                         # User is asking for a comedy
                        .new_turn(SysActFactory(SysActionType.Confirm)      # System confirming that they're looking for a specific movie, not a suggestion
                            .confirm('looking_for_specific_movie')
                            .genre('comedy')    
                            .build())
                        .deny()                                             # User answering negatively
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.ShowRecommendation)  # System suggesting a comedy movie
                            .id(any=True)
                            .title(any=True)
                            .overview(any=True)
                            .year(any=True)
                            .rating(any=True)
                            .genre(containing='comedy')    
                            .build()
            }
        },
        {
            'input': BeliefStateFactory()
                        .inform('genres', 'comedy')                         # User is asking for a comedy
                        .new_turn(SysActFactory(SysActionType.Confirm)      # System confirming that they're looking for a specific movie, not a suggestion
                            .confirm('looking_for_specific_movie')
                            .genre('comedy')    
                            .build())
                        .affirm()                                           # User answering affirmatively
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Request)             # System asking the user to fill another slot, as just one is not enough to find a specific movie
                            .actor()
                            .build()
            }
        }
    ]