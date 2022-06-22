def load_movie_nlu_test():
    from examples.webapi.movie import MovieNLU, MovieDomain, get_nlu_tests
    domain = MovieDomain()
    nlu = MovieNLU(domain=domain)
    return nlu, get_nlu_tests()

if __name__ == '__main__':
    nlu, tests = load_movie_nlu_test()
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

    print(f'{successful_test_count}/{len(tests)} TESTS SUCCESSFUL')
