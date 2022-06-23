from utils.sysact import SysAct, SysActionType
from .test_utils import SysActFactory

def get_nlg_tests():
    return [
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('Top Gun')
                        .year('1986')
                        .actor('Tom Cruise')            
                        .build(), 
            'expected_output': {'sys_utterance': 'The movie Top Gun starring Tom Cruise was released in 1986.'}
        },
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('Top Gun')
                        .build(), 
            'expected_output': {'sys_utterance': 'I found the movie Top Gun. What do you want to know about it?'}
        },
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('Top Gun')
                        .rating('8')
                        .build(), 
            'expected_output': {'sys_utterance': 'The movie Top Gun is rated 8.'}
        },
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('Top Gun')
                        .year('1986')
                        .genre('action')
                        .actor('Tom Cruise') 
                        .overview('OVERVIEW') 
                        .rating('8')          
                        .build(), 
            'expected_output': {'sys_utterance': "The action movie Top Gun released in 1986 starring Tom Cruise is rated 8. Here's a short description: OVERVIEW"}
        },
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('Top Gun')
                        .genre('action')
                        .build(), 
            'expected_output': {'sys_utterance': "Top Gun is an action movie."}
        },
        {
            'input': SysActFactory(SysActionType.InformByName)
                        .title('The Hangover')
                        .genre('comedy')
                        .build(), 
            'expected_output': {'sys_utterance': "The Hangover is a comedy movie."}
        }
    ]