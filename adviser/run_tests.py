import argparse

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

def run_nlu_tests(nlu, tests):
    successful_test_count = 0
    for test in tests:
        input = test['input']
        output = nlu.extract_user_acts(input)['user_acts']

        expected_output = test['expected_output']

        missing_acts = []
        for act in expected_output:
            if act in output:
                output.remove(act)
            else:
                missing_acts.append(act)

        if len(missing_acts) > 0:
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

        output = nlg.generate_system_utterance(sys_act=input)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ADVISER 2.0 Dialog System Test Runner')
    parser.add_argument('domain', choices=['movies'],
                        nargs='?',
                        help="Chat domain to test. \n",
                        default="movies")
    parser.add_argument('-m', '--module', 
                        choices=['nlu', 'nlg', 'all'], 
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

    
