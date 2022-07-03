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
        },
        {
            'input': SysActFactory(SysActionType.Confirm)
                        .confirm('looking_for_specific_movie')
                        .genre('comedy')
                        .build(), 
            'expected_output': {'sys_utterance': "Are you looking for a specific comedy movie?"}
        },
        {
            'input': SysActFactory(SysActionType.InformByAlternatives)
                        .title('Movie 1')
                        .title('Movie 2')
                        .title('Movie 3')
                        .build(), 
            'expected_output': {'sys_utterance': "I've found 3 movies. Which one do you want to know more about? \n1) 'Movie 1'\n2) 'Movie 2'\n3) 'Movie 3'"}
        },
        {
            'input': SysActFactory(SysActionType.InformByAlternatives)
                        .title('Movie 1')
                        .title('Movie 2')
                        .title('Movie 3')
                        .result_count(10)
                        .build(), 
            'expected_output': {'sys_utterance': "I've found 10 movies. The 3 most popular ones are: \n1) 'Movie 1'\n2) 'Movie 2'\n3) 'Movie 3'\nWhich one do you want to know more about?"}
        }
    ]