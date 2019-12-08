"""Keyword Search Test
Author: Joona Ruutiainen
Last edit: 7.12.2019

This script is part of an excersise project for the course 'TIE-21201 Ohjelmistojen testaus'
in Tampere University. The purpose of the project is to perfom tests for a photo album web application
based on a pre-made testing plan (doing the plan was part 1 of the project). Performing the test requires 
having the actual web application running in the background.

This module performs tests to web application's searchbar functionality on Google Chrome with different keyword
searches. Helium's python library (heliumhq.com) is used to perform functions of the application in browser.
Test cases, which are based on given requirements specification, are read from 'test-cases.json' and
the results of the test are written into 'test-log.txt'. 
"""

import string
import json
from helium.api import *

USERNAME = 'user'
PASSWORD = 'password'
APP_URL = 'http://localhost:8080/ps/v2/index.html'
TEST_JSON = 'test-cases.json'
TEST_LOG = 'test-log.txt'
TEST_KEYWORDS = {}
TEST_CASES = []

class TestInput:
    """
    A class that is used to represent test cases of this test

    Attributes
    ----------
    msg : str
        a short description of the test case that is printed into test log
    keywords : list[str]
        a list of keywords used in the search (default is an empty list)
    expected_results : int, optional
        the number of expected results from the image search (default is 0)
    results_found : int
        the number of found images from the image search (default is 0)
    errors : int
        the number of web application's errors found with this test case (default is 0)
    """
    def __init__(self, msg, keywords=[], results_expected=0):
        self.msg = msg
        self.keywords = keywords
        self.results_expected = results_expected
        self.results_found = 0
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
                test_case['keywords'],
                test_case['results_expected'],
            )
            TEST_CASES.append(new_test)
        log.write('Added {} test cases \n'.format(len(TEST_CASES)))
        return True
    except:
        log.write('Failed to initialize test cases \n')
        print('Failed to initialize test cases')
        return False

def initialize_keywords(log):
    """Populates the TEST_KEYWORDS dict, keyword as a name and list of IDs as a value
    Returns true if initialization succeeded or false if there was an error

    Parameters
    ----------
    log : file
        the file to write into, which needs to be opened before calling this function
    """
    try:
        """In this test all the images with keywords are located in the first page of the album view
        """
        TEST_KEYWORDS['aaa'] = [0,1,2]
        TEST_KEYWORDS['bbb'] = [3,4,5]
        TEST_KEYWORDS['ccc'] = [6,7]
        return True
    except:
        log.write('Failed to initialize keywords \n')
        print('Failed to initialize keywords')
        return False

def add_keywords():
    try:
        loaded_images = find_all(S('div > p > img'))
        for keyword in TEST_KEYWORDS:
            for id in TEST_KEYWORDS[keyword]:
                click(loaded_images[id].web_element)
                write(keyword, into='Syötä avainsanat pilkulla (,) erotettuna.')
                click(S('#view-full-save-keywords'))
                click(S('#view-full-close'))
    except:
        return False
    return True

def test_search_with_keywords(testObject, log):
    """The main testing function of this module. A search action to web application is performed
    in this function and the response of the application is validated and written into the test log.
    Returns true if there were errors found in the application, or false if there was no errors or
    the test didnt complete

    Parameters
    ----------
    testObject : TestInput object
        test case specifications used in the search are read from the given TestInput object
    log : file
        the file to write into, which needs to be opened before calling this function
    """
    try:
        search_input = ''
        for keyword in testObject.keywords:
            if search_input == '':
                search_input += keyword
            else:
                search_input += ',' + keyword
        write(search_input, into='Type keywords for search, separated by comma (,)')
        click(S('#view-search'))
    except:
        log.write('Search failed \n')
        return False
    
    try:
        """When a search is performed on the web application's album view, page is reloaded and
        populated with images that match the given specifications. In this test script these images
        are recognized by taking the 'id-attribute' of a loaded image and checking if the said 
        image was supposed to be loaded in this search.
        """
        loaded_images = find_all(S('div > p > img'))
    except:
        log.write('Failed to load page elements \n')
        return False

    for image in loaded_images:
        testObject.results_found += 1
        id = image.web_element.get_attribute('id')
        match_not_found = True
        for keyword in testObject.keywords:
            if keyword in TEST_KEYWORDS:
                if(int(id) in TEST_KEYWORDS[keyword] and testObject.results_expected != 0 ):
                    log.write('IMAGE_ID: {} OK \n'.format(id))
                    match_not_found = False
        if match_not_found:
            log.write('IMAGE_ID: {} ERROR \n'.format(id))
            testObject.errors += 1

    if testObject.results_found != testObject.results_expected:
        testObject.errors += 1
        log.write('Expected {} results, got {} \n'.format(testObject.results_expected, testObject.results_found))
    if testObject.errors == 1:
        log.write('Search completed with 1 error \n')
    else:
        log.write('Search completed with {} errors \n'.format(testObject.errors))
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
            '------  KEYWORD SEARCH TEST ------ \n',
            '---------------------------------- \n',
            '# Initializing test \n',
            '\n'
        ])
        print('# Initializing test')
        if initialize_keywords(test_log) and initialize_test_cases(test_log):
            test_log.write('\n')
            test_log.write('# Starting Chrome \n')
            print('# Starting Chrome')
            start_chrome(APP_URL)
            try:
                write(USERNAME, into='username')
                write(PASSWORD, into='password')
                click('Login')
            except:
                test_log.write('Failed to login \n')
            if add_keywords():
                test_log.write('# Going through test cases \n')
                print('# Going through test cases')
                failed_tests = 0
                for test_case in TEST_CASES:
                    refresh()
                    test_log.write('\n')
                    test_log.write(test_case.msg + '\n')
                    try:
                        write(USERNAME, into='username')
                        write(PASSWORD, into='password')
                        click('Login')
                    except:
                        test_log.write('Failed to login \n')
                        break
                    errors = test_search_with_keywords(test_case, test_log)
                    if errors:
                        failed_tests += 1
            else:
                test_log.write('Failed to add keywords for images \n')
                print('Failed to add keywords for images')
                failed_tests = len(TEST_CASES)
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