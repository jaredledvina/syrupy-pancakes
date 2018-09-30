#!/usr/bin/env python3
'''
Syrupy Pancackes is a collection of Selenium and BeautifulSoup based helpers
to automate the laborious actions needed to schedule flying lessions
via https://skymanager.com
'''

import logging
import sys

from selenium import webdriver
from bs4 import BeautifulSoup

URL = 'https://umflyers.skymanager.com/'
USERNAME = ''
PASSWORD = ''
DATE = '2018-10-08'
INSTRUCTOR='J. Jayne'
TIME = ''

LOG = logging.getLogger('syrupy-pancakes')


def setup():
    '''Returns Selenium driver'''
    LOG.debug('Attempting to access {}'.format(URL))
    driver = webdriver.Chrome()
    driver.get(URL)
    return driver


def login(driver):
    '''Logs into SkyManager'''
    LOG.info('Logging into {} as user {}'.format(URL, USERNAME))
    username = driver.find_element_by_id('Username')
    username.send_keys(USERNAME)
    password = driver.find_element_by_id('Password')
    password.send_keys(PASSWORD)
    remeberme = driver.find_element_by_name('RememberMe')
    remeberme.click()
    login = driver.find_element_by_xpath("//input[@type='submit']")
    login.click()


def navigate_schedule(driver, date):
    '''Navigates the SkyManager schedule'''
    schedule = driver.find_element_by_partial_link_text('ONLINE SCHEDULE')
    schedule.click()
    # HACK to jump to the right date page, we _could_ navigate this
    # horrendous UI but, this should work for now
    LOG.debug('Attempting to open schedule for date {}'.format(date))
    driver.get(URL + 'Schedule/Day/' + date)

def validate_length(name, iterable, length, operation='!='):
    '''Exists if something isnt the length'''
    if eval('{} {} {}'.format(len(iterable), operation, length)):
        LOG.error('Failing, because the length of {} {} {}'.format(name, operation, length))
        sys.exit(2)
    return True


def cleanup_schedule(driver):
    '''Returns a cleaned up version of the schedule'''
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # First, grab the time schedule table
    tables = soup.find_all('table', attrs={'onclick': 'ResHelper.AddReservation(event);'})
    validate_length('schedule table', tables, 1)
    table = tables[0]
    # Pull out the tables body
    table_body = table.find_all('tbody')
    validate_length('schedule table body', table_body, 1)
    # Ensure there's only 1 time row
    timerows = table.find_all('tr', attrs={'id': 'topTimelineMark'})

    validate_length('time rows', timerows, 1)
    #TODO: Replace validate_length with assert
    #assert len(timerows) == 1, 'Failing because of time rows'

    timerow = timerows[0]
    # Ensure we find more than one aircraft
    aircrafts = table.find_all('tr', attrs={'class': 'aircraft'})
    validate_length('aircrafts', aircrafts, 2, '<=')
    # Ensure we find one instructor
    instructors = table.find_all('tr', attrs={'class': 'instructor'})
    validate_length('instructors', instructors, 1)
    instructor = instructors[0]


    # Begin building not shit table data
    availible_times = {}
    for column in timerow.find_all('td'):
        availible_times[column.text.strip()] = {}
    instructor_name = instructor.find_all('td')[0].find_all('a')[0].text.strip()
    # Get instructor schedule
    schedule = instructor.find_all('td', attrs={'class': ['Off', 'Pending', 'L', 'R', 'CheckedIn', 'CheckedOut']})
    # Ideas:
    # Iterate through table, find rows for:
    # //*[@id="topTimelineMark"]
    # #minibannerbody > div.schedule > table > tbody > tr.instructor
#{
#  '8a': {
#    'aircrafts': [
#      'n222um',
#      'n333um',
#      'n68334',
#      'n4614b'
#    ],
#    'instructors' [
#      'J. Jayne',
#    ]
#  }
#}
def find_instructor_times(driver):
    '''Attempts to find open timeslots for a lesson'''
    LOG.debug('Attempting to find all instructors')
    instructors = driver.find_elements_by_class_name('instructor')
    potential_instructors = []
    for instructor in instructors:
        if INSTRUCTOR in instructor.text.split('\n')[0]:
            potential_instructors.append(instructor)
    if len(potential_instructors) != 1:
        LOG.error('Failing as we found more than one instructor: {}'.format(
                  [instructor.text for instructor in potential_instructors]))
        sys.exit(2)
    return potential_instructors


def find_planes(driver, time):
    '''Attempts to find the best plane for a lesson'''
    aircrafts = driver.find_elements_by_class_name('aircraft')
    for aircraft in aircrafts:
        pass

def setup_logging(args):
    '''Configures the global LOG bits'''
    if args.verbose:
        LOG.setLevel('DEBUG')
    else:
        LOG.setLevel('INFO')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    LOG.addHandler(ch)


def parse_args():
    '''Helps make this a commandline interface'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enable debug messages')
    args = parser.parse_args()
    return args


def main():
    '''Master of all'''
    args = parse_args()
    setup_logging(args)
    driver = setup()
    login(driver)
    navigate_schedule(driver, DATE)


if __name__ == '__main__':
    main()
