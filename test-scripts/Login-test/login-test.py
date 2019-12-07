"""Login Test
Author: Joona Ruutiainen
Last edit: 19.11.2019

This script is part of an excersise project for the course 'TIE-21201 Ohjelmistojen testaus'
in Tampere University. The purpose of the project is to perfom tests for a photo album web application
based on a pre-made testing plan (doing the plan was part 1 of the project). Performing the test requires 
having the actual web application running in the background.

This module performs tests to web application's login functionality on Google Chrome.
Helium's python library (heliumhq.com) is used to perform functions of the application in browser.
Test cases, which are based on given requirements specification, are read from 'test-cases.json' and
the results of the test are written into 'test-log.txt'. 
"""

import json
from helium.api import *

TEST_JSON = 'test-cases.json'
TEST_LOG = 'test-log.txt'
TEST_CASES = []

class TestInput:
    """
    A class that is used to represent test cases of this test

    Attributes
    ----------
    msg : str
        a short description of the test case that is printed into test log
    username : str
        a string that is inserted into application's username field
    password : str
        a string that is inserted into application's password field
    errors : int
        the number of web application's errors found with this test case (default is 0)
    """
    def __init__(self, msg, username, password):
        self.msg = msg
        self.username = username
        self.password = password
        self.errors = 0

def initialize_test_cases(log):
    """Reads the test-case-data from a JSON-file and saves it as TestInput objects in TEST_CASES
    Returns true if initialization succeeded or false if there was an error

    Parameters
    ----------
    log : file
        the file to write into, which needs to be opened before calling this function
    """
    try:
        file = open(TEST_JSON, 'r')
        test_data = json.load(file)
        file.close()
        for test_case in test_data:
            new_test = TestInput(
                test_case['msg'],
                test_case['username'],
                test_case['password']
            )
            TEST_CASES.append(new_test)
        log.write('Added {} test cases \n'.format(len(TEST_CASES)))
        return True
    except:
        log.write('Failed to initialize test cases \n')
        print('Failed to initialize test cases')
        return False

def test_login(testObject, log):
    """The main testing function of this module. A login action to web application is performed
    in this function and the response of the application is validated and written into the test log.
    Returns true if there were errors found in the application, or false if there was no errors or
    the test didnt complete

    Parameters
    ----------
    testObject : TestInput object
        test case specifications used in the login are read from the given TestInput object
    log : file
        the file to write into, which needs to be opened before calling this function
    """
    write(testObject.username, into='username')
    write(testObject.password, into='password')
    click('Login')
    if ( testObject.username=='user' and testObject.password=='password' ):
        if ( len(find_all(Image())) == 0 ):
            log.write('Test case failed: {} \n'.format(testObject.msg))
            testObject.errors += 1
        else:
            log.write('Test case passed: {} \n'.format(testObject.msg))
    else:
        if ( len(find_all(Image())) == 0):
            log.write('Test case passed: {} \n'.format(testObject.msg))
        else:
            log.write('Test case failed: {} \n'.format(testObject.msg))
            testObject.errors += 1
    refresh()
    if testObject.errors > 0:
        return True
    return False

def main():
    """Main function of the module, in which the test-log file is opened (and closed) and all 
    the TEST_CASES are iterated through and performed a search test to. 
    """
    try:
        test_log = open(TEST_LOG, 'w')
        test_log.writelines([
            '---------------------------------- \n',
            '----------- LOGIN TEST ----------- \n',
            '---------------------------------- \n',
            '# Initializing test \n',
            '\n'
        ])
        print('# Initializing test')
        if initialize_test_cases(test_log):
            test_log.write('\n# Starting Chrome \n')
            print('# Starting Chrome')
            start_chrome('http://localhost:8080/ps/v1/index.html')
            test_log.write('# Going through test cases \n \n')
            print('# Going through test cases')
            failed_tests = 0
            for test_case in TEST_CASES:
                if test_login(test_case, test_log):
                    failed_tests += 1
            test_log.write('\n')
            test_log.write('# Closing Chrome \n')
            print('# Closing Chrome')
            kill_browser()
            test_log.writelines([
                '---------------------------------- \n',
                '---------- TEST RESULTS ---------- \n',
                '---------------------------------- \n',
                '# Test completed with {} failed test cases (out of {})'.format(failed_tests, len(TEST_CASES))
            ])
        else:
            test_log.write('\n')
            test_log.write('# Test aborted')
            print('# Test aborted')
        test_log.close()
        print('# Test completed')
    except OSError:
        print('Error in writing text log')

main()
