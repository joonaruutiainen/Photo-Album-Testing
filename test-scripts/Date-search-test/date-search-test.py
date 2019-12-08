"""Date Search Test
Author: Joona Ruutiainen
Last edit: 7.12.2019

This script is part of an excersise project for the course 'TIE-21201 Ohjelmistojen testaus'
in Tampere University. The purpose of the project is to perfom tests for a photo album web application
based on a pre-made testing plan (doing the plan was part 1 of the project). Performing the test requires 
having the actual web application running in the background.

This module performs tests to web application's searchbar functionality on Google Chrome with different date
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
TEST_IMAGES = []
TEST_CASES = []

class TestInput:
    """
    A class that is used to represent test cases of this test

    Attributes
    ----------
    msg : str
        a short description of the test case that is printed into test log
    start_date : str
        input used in the searchbar's 'start date' field (expected to be RFC3339 date format)
    end_date : str
        input used in the searchbar's 'end date' field (expected to be RFC3339 date format)
    results_expected : int, optional
        the number of expected results from the image search (default is 0)
    results_found : int
        the number of found images from the image search (default is 0)
    errors : int
        the number of web application's errors found with this test case (default is 0)
    """
    def __init__(self, msg, start_date='', end_date='', results_expected=0):
        self.msg = msg
        self.start_date = start_date
        self.end_date = end_date
        self.results_expected = results_expected
        self.results_found = 0
        self.errors = 0

class Image:
    """
    A class that is used to represent pre-set images in the web application's photo album
    
    Attributes
    ----------
    id : int
        the id of the image
    date : str
        the date when the image was 'uploaded' in the album
    """
    def __init__(self, id, date):
        self.id = id
        self.date = date

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
                test_case['start_date'],
                test_case['end_date'],
                test_case['results_expected']
            )
            TEST_CASES.append(new_test)
        log.write('Added {} test cases \n'.format(len(TEST_CASES)))
        return True
    except:
        log.write('Failed to initialize test cases \n')
        print('Failed to initialize test cases')
        return False

def initialize_images(log):
    """Populates the TEST_IMAGES list with Image items that are dated starting from 
    01.06.2018 12:00:00 to 19.07.2018 12:00:00 in 24 hour intervals, 49 images in total
    Returns true if initialization succeeded or false if there was an error

    Parameters
    ----------
    log : file
        the file to write into, which needs to be opened before calling this function
    """
    try:
        for i in range(30):
            if i < 9:
                date = '2018-06-0{:n}T12:00:00Z'.format(i+1)
                TEST_IMAGES.append(Image(str(i+1),date))
            else:
                date = '2018-06-{:n}T12:00:00Z'.format(i+1)
                TEST_IMAGES.append(Image(str(i+1),date))
        for i in range(19):
            if i < 9:
                date = '2018-07-0{:n}T12:00:00Z'.format(i+1)
                TEST_IMAGES.append(Image(str(i+1+30), date))
            else:
                date = '2018-07-{:n}T12:00:00Z'.format(i+1)
                TEST_IMAGES.append(Image(str(i+1+30), date))
        log.write('Added {} images \n'.format(len(TEST_IMAGES)))
        return True
    except:
        log.write('Failed to initialize images \n')
        print('Failed to initialize images')
        return False

def get_image_date(id):
    """Returns the date of an image with the given ID or 'No image with given ID'

    Parameters
    ----------
    id : int
        id of the image
    """
    for image in TEST_IMAGES:
        if image.id == id:
            return image.date
    return 'No image with given ID'

def compare_start_date(id, date):
    """Returns true if the date of an image with the given ID is AFTER the given date, or false if its not
    Date comparisons are made with strings that are expected to be in RFC3339 date format

    Parameters
    ----------
    id : int
        id of the image
    date : str
        date to be compared to
    """
    if date == '':
        date += '2018-05-31T12:00:00Z'
    return get_image_date(id) >= date

def compare_end_date(id, date):
    """Returns true if the date of an image with the given ID is BEFORE the given date, or false if its not
    Date comparisons are made with strings that are expected to be in RFC3339 date format

    Parameters
    ----------
    id : int
        id of the image
    date : str
        date to be compared to
    """
    if date == '':
        date += '2018-07-20T12:00:00Z'
    return get_image_date(id) <= date

def test_search_with_date(testObject, log, next_page=False):
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
    next_page : bool
        if true, the function is being called recursively for the next page of the search results
        and the search is not performed again (default is false)
    """
    if not next_page:
        try:         
            write(testObject.start_date, into='Type start date in RFC3339 format')
            write(testObject.end_date, into='Type end date in RFC3339 format')
            click(S('#view-search'))
        except:
            log.write('Search failed \n')
            return False
    
    try:
        """When a search is performed on the web application's album view, page is reloaded and
        populated with images that match the given specifications. In this test script these images
        are recognized by taking the 'src-attribute' of a loaded image and separating an ID from the url.
        Then they are compared to an image in TEST_IMAGES with that ID and checking if the said 
        image was supposed to be loaded in this search.
        """
        loaded_images = find_all(S('div > p > img'))
        first_result = loaded_images[0].web_element.get_attribute('src')
    except:
        log.write('Failed to load page elements \n')
        return False

    for image in loaded_images:
        testObject.results_found += 1
        id = image.web_element.get_attribute('src').split('/')
        id = id[6].split('.')[0]
        if  (compare_start_date(id, testObject.start_date) 
            and compare_end_date(id, testObject.end_date)
            and testObject.results_expected != 0 ):
            log.write('IMAGE_ID: {} DATE: {} OK \n'.format(id, get_image_date(id)))
        else:
            log.write('IMAGE_ID: {} DATE: {} ERROR \n'.format(id, get_image_date(id)))
            testObject.errors += 1

    try:       
        click(S('#view-next'))
        loaded_images = find_all(S('div > p > img'))
        if first_result != loaded_images[0].web_element.get_attribute('src'):
            return test_search_with_date(testObject, log, True)
        else:
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
    except:
        print('Failed to load the next page \n')
        return False

def main():
    """Main function of the module, in which the test-log file is opened (and closed) and all 
    the TEST_CASES are iterated through and performed a search test to. 
    """
    try:
        test_log = open(TEST_LOG, 'w')
        test_log.writelines([
            '---------------------------------- \n',
            '-------- DATE SEARCH TEST -------- \n',
            '---------------------------------- \n',
            '# Initializing test \n',
            '\n'
        ])
        print('# Initializing test')
        if initialize_images(test_log) and initialize_test_cases(test_log):
            test_log.write('\n')
            test_log.write('# Starting Chrome \n')
            print('# Starting Chrome')
            start_chrome(APP_URL)
            test_log.write('# Going through test cases \n')
            print('# Going through test cases')
            failed_tests = 0
            for test_case in TEST_CASES:
                test_log.write('\n')
                test_log.write(test_case.msg + '\n')
                try:
                    write(USERNAME, into='username')
                    write(PASSWORD, into='password')
                    click('Login')
                except:
                    test_log.write('Failed to login \n')
                    break
                errors = test_search_with_date(test_case, test_log)
                if errors:
                    failed_tests += 1
                refresh()
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