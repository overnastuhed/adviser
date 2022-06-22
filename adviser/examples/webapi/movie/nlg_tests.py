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
            'expected_output': {'sys_utterance': 'The movie Top Gun starring Tom Cruise was released in 1986'}
        }
    ]