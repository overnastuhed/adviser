import argparse
import traceback

def load_movie_nlu_tests():
    from examples.webapi.movie import MovieNLU, MovieDomain, get_nlu_tests
    domain = MovieDomain()
    nlu = MovieNLU(domain=domain)
    return nlu, get_nlu_tests()

def load_movie_nlg_tests():
    from examples.webapi.movie import MovieNLG, MovieDomain, get_nlg_tests
    domain = MovieDomain()
    nlg = MovieNLG(domain=domain)
    return nlg, get_nlg_tests()

def load_movie_policy_tests():
    from examples.webapi.movie import MoviePolicy, MovieDomain, get_policy_tests
    domain = MovieDomain()
    policy = MoviePolicy(domain=domain)
    return policy, get_policy_tests()


def run_nlu_tests(nlu, tests):
    successful_test_count = 0
    for test in tests:
        input = test['input']
        
        if type(input) is tuple:
            nlu.save_last_sys_act(sys_act=input[1])
            output = nlu.extract_user_acts(user_utterance=input[0])['user_acts']
        else:
            output = nlu.extract_user_acts(input)['user_acts']

        try:
            expected_output = test['expected_output']
        except Exception as e:
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            print('Failed with exception: ')
            print(e)
            print(traceback.format_exc())
            print('-------------------------------------------')
            continue

        missing_acts = []
        for act in expected_output:
            if act in output:
                output.remove(act)
            else:
                missing_acts.append(act)

        if len(missing_acts) > 0 or len(output) > 0:
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            if len(missing_acts) > 0:
                print('Missing acts:')
                print(missing_acts)
            if len(output) > 0:
                print('Extraneous acts:')
                print(output)
            print('-------------------------------------------')
        else:
            successful_test_count += 1
    print(f'{successful_test_count}/{len(tests)} NLU TESTS SUCCESSFUL')

def run_nlg_tests(nlg, tests):
    successful_test_count = 0
    for test in tests:
        input = test['input']
        expected_output = test['expected_output']

        try:
            output = nlg.generate_system_utterance(sys_act=input)
        except Exception as e:
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            print('Failed with exception: ')
            print(e)
            print(traceback.format_exc())
            print('-------------------------------------------')
            continue

        if expected_output != output:
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            print('Expected output: ')
            print(expected_output)
            print('Actual output: ')
            print(output)
            print('-------------------------------------------')
        else:
            successful_test_count += 1
    print(f'{successful_test_count}/{len(tests)} NLG TESTS SUCCESSFUL')

def compare_system_acts(a, b):
    if a is None or b is None:
        return False
    if a.type != b.type:
        return False
    if len(a.slot_values) != len(b.slot_values):
        return False
    for slot in a.slot_values.keys():
        if slot not in b.slot_values:
            return False
        a_value = a.slot_values[slot]
        b_value = b.slot_values[slot]

        if len(a_value) > 1 or len(b_value) > 1:
            for b_val in b_value:
                if b_val not in a_value and "*" not in a_value:
                    return False
        elif a_value != b_value and a_value != ['*'] and b_value != ['*']:
            return False
    return True

def run_policy_tests(policy, tests):
    successful_test_count = 0
    for test in tests:
        input = test['input']
        expected_output = test['expected_output']

        try:
            output = policy.choose_sys_act(beliefstate=input)
        except Exception as e:
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            print('Failed with exception: ')
            print(e)
            print(traceback.format_exc())
            print('-------------------------------------------')
            continue


        if not compare_system_acts(expected_output['sys_act'], output['sys_act']):
            print('---------------FAILED TEST-----------------')
            print('Input: ', input)
            print('Expected output: ')
            print(expected_output)
            print('Actual output: ')
            print(output)
            print('-------------------------------------------')
        else:
            successful_test_count += 1
    print(f'{successful_test_count}/{len(tests)} POLICY TESTS SUCCESSFUL')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ADVISER 2.0 Dialog System Test Runner')
    parser.add_argument('domain', choices=['movies'],
                        nargs='?',
                        help="Chat domain to test. \n",
                        default="movies")
    parser.add_argument('-m', '--module', 
                        choices=['nlu', 'nlg', 'policy', 'all'], 
                        help="Dialog system modules to test.\n",
                        default="all")
    args = parser.parse_args()

    domain = args.domain
    module = args.module

    if args.module == 'nlu' or args.module == 'all':
        if args.domain == 'movies':
            nlu, tests = load_movie_nlu_tests()
        else:
            raise NotImplementedError
        run_nlu_tests(nlu, tests)

    if args.module == 'nlg' or args.module == 'all':
        if args.domain == 'movies':
            nlg, tests = load_movie_nlg_tests()
        else:
            raise NotImplementedError
        run_nlg_tests(nlg, tests)

    if args.module == 'policy' or args.module == 'all':
        if args.domain == 'movies':
            policy, tests = load_movie_policy_tests()
        else:
            raise NotImplementedError
        run_policy_tests(policy, tests)

    
