from utils.sysact import SysActionType
from .test_utils import SysActFactory, BeliefStateFactory

def get_policy_tests():
    return [
        {
            'input': BeliefStateFactory().build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Welcome).build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('primary_release_year', '1986')
                        .inform('with_genres', 'action')
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.Request)
                            .actor()            
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('primary_release_year', '1986')
                        .inform('with_genres', 'action')
                        .inform('with_actors', 'Tom Cruise')                
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.InformByName)
                            .id('0')
                            .title('Top Gun')    
                            .overview("For Lieutenant Pete 'Maverick' Mitchell and his friend and co-pilot Nick 'Goose' Bradshaw, being accepted into an elite training school for fighter pilots is a dream come true. But a tragedy, as well as personal demons, will threaten Pete's dreams of becoming an ace pilot.")        
                            .year('1986')
                            .genre('action')
                            .actor('Tom Cruise')
                            .build()
                        }
        },
        {
            'input': BeliefStateFactory()
                        .inform('primary_release_year', '1986')
                        .inform('with_genres', 'action')
                        .inform('with_actors', 'Tom Cruise')    
                        .request_alternative()            
                        .build(), 
            'expected_output': {
                'sys_act': SysActFactory(SysActionType.InformByAlternatives)
                            .id('none') # no alternative found, no other movie besides Top Gun matches this criteria
                            .year('1986')
                            .genre('action')
                            .actor('Tom Cruise')
                            .build()
                        }
        }
    ]