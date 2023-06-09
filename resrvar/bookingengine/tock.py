from bookingengine.resplatform import ResPlatform
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

class Tock(ResPlatform):

    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%I:%M %p'
    FMT = '{} {}'.format(DATE_FMT, TIME_FMT)

    def __init__(self, *args, **kwargs):


        self.venue_name = kwargs.get('venue_name')
        self.venue_id = kwargs.get('venue_id')
        self.party_size = kwargs.get('party_size')
        self.res_type = kwargs.get('res_type')

        if self.venue_name is None or self.venue_id is None:
            raise TypeError
        if self.party_size is None or self.res_type is None:
            raise TypeError


        # TODO: Make this platform agnostic
        CHROME_PATH = 'chromedriver_mac64/chromedriver'
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH, options=options)
        self.wait = WebDriverWait(self.driver, 5)

        super().__init__(None)

    def authenticate(self, *args, **kwargs):
        username = kwargs.get('tock_email')
        auth_token = kwargs.get('tock_token')

        if username is None or auth_token is None:
            raise TypeError

        url = 'https://www.exploretock.com/login'
        self.driver.get(url)
        email_input = self.wait.until(ec.presence_of_element_located((By.ID, 'email')))
        email_input.send_keys(username)
        pass_input = self.wait.until(ec.presence_of_element_located((By.ID, 'password')))
        pass_input.send_keys(auth_token)
        self.driver.find_element(By.XPATH, '//section/button').click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, '//main/div/div/div[2]')))

    def book(self, preferred_slot):
        return True, "12345"
        if not self.select_time(preferred_slot):
            logging.info('Preferred time of {} not available'.
                         format(datetime.strftime(preferred_slot, self.FMT)))
            days = self.get_available_dates()
            time_slots = self.get_available_times(days)
            if len(time_slots) > 1:
                selected_slot = self.de.select_preferred_time(time_slots)
                logging.info('Decision Engine selected time of {}'
                             .format(datetime.strftime(selected_slot, self.FMT)))
                self.select_time(selected_slot)
            else:
                return False, ''
        self.update_profile()
        return True, '1234'
        self.complete_booking()
        self.close_questionnaire()
        confirmation = self.get_confirmation()
        return True, confirmation


    def get_available_times(self):
        days = self.get_available_dates()
        times = self.get_times_for_days(days)
        return times

    def get_available_dates(self):
        self.open_calendar(datetime.today())

        cal_xpath = '//div[@id="experience-dialog-content"]//div[@class="SearchBarMonths"]'
        cal_element = self.wait.until(ec.presence_of_element_located((By.XPATH, cal_xpath)))

        available_dates = []
        available_xpath = './/button[contains(@class,"is-available") and contains(@class,"is-in-month")]'

        available_elements = cal_element.find_elements(By.XPATH, available_xpath)

        available_dates = []
        for element in available_elements:
            date_str = element.get_attribute('aria-label')
            available_dates.append(date_str)

        return available_dates

    def get_times_for_days(self, available_dates):
        # We are assuming get_available_dates was called right before this and we're on the same page

        times_xpath = '//div[@id="experience-dialog-content"]//div[@class="SearchModal-body"]'
        times_container = self.wait.until(ec.presence_of_element_located((By.XPATH, times_xpath)))
        available_times = []
        for day in available_dates:
            #Click on available date
            date_xpath = '//div[@id="experience-dialog-content"]//div[@class="SearchBarMonths"]' \
                        '//button[@aria-label="{}" and contains(@class,"is-in-month")]'.format(day)

            self.driver.find_element(By.XPATH, date_xpath).click()
            # Wait until modal finishes loading
            modal_xpath = '//div[@class="SearchModalExperience is-animating"]'
            self.wait.until(ec.presence_of_element_located((By.XPATH, times_xpath + modal_xpath)))
            # Get available time slots
            available_elements = times_container.find_elements(By.XPATH, './/div/div/button')
            for element in available_elements:
                time_str = element.find_element(By.XPATH, './/span/span/span').get_attribute('innerText')
                time_slot_str = '{} {}'.format(day, time_str)
                time_slot = datetime.strptime(time_slot_str, self.FMT)
                available_times.append(time_slot)

        return available_times

    def open_calendar(self, day):
        # TODO: Check if calendar is already open on current date
        # TODO: Change date if open and not on current daete
        res_time = '20%3A00'

        url = 'https://www.exploretock.com/{}/experience/{}/{}?date={}&size={}&time={}'.format(
            self.venue_name,
            self.venue_id,
            self.res_type,
            day.strftime(self.DATE_FMT),
            self.party_size,
            res_time)

        self.driver.get(url)


    def select_time(self, time_slot):

        self.open_calendar(time_slot)

        res_day = time_slot.strftime(self.DATE_FMT)
        res_time = time_slot.strftime('%-I:%M %p')
        cal_xpath = '//div[@id="experience-dialog-content"]//div[@class="SearchBarMonths"]'
        cal_element = self.wait.until(ec.presence_of_element_located((By.XPATH, cal_xpath)))

        date_xpath = './/button[contains(@class,"is-available")' \
                ' and contains(@class,"is-in-month")' \
                ' and @aria-label="{}"]'.format(res_day)

        time_xpath = '//div[@class="SearchModalExperience is-animating"]' \
                '//button/span/span/span[text()="{}"]'.format(res_time)

        # TODO: Rather than waiting for the preferred time to load
        # Get list of all times for the day and compare
        # Allow for ~30 min diff on each side

        try:
            self.wait.until(ec.presence_of_element_located((By.XPATH, date_xpath))).click()
            self.wait.until(ec.presence_of_element_located((By.XPATH, time_xpath))).click()
            return True
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            return False

    def update_profile(self):
        self.wait.until(ec.presence_of_element_located((By.XPATH, '//h1[text() = "Your profile"]')))

        button_xpath = '//main//form//button[@type="submit"]'
        button_element = self.wait.until(ec.presence_of_element_located((By.XPATH, button_xpath)))
        button_element.click()

    def complete_booking(self):

        self.wait.until(ec.presence_of_element_located(
            (By.XPATH,' //h1[text() = "Complete your reservation"]')
            ))

        #sms_box = self.wait.until(ec.presence_of_element_located((By.ID, 'consentsToSMS')))
        #sms_box.click()

        complete_button_xpath = '//button//span[text()="Complete reservation"]'
        self.wait.until(ec.presence_of_element_located((By.XPATH, complete_button_xpath))).click()

    def close_questionnaire(self):
        try:
            close_button_xpath = '//button[@aria-label="Close"]/span'
            self.wait.until(ec.presence_of_element_located((By.XPATH, close_button_xpath))).click()
        except (TimeoutException, StaleElementReferenceException):
            pass

    def get_confirmation(self):
        confirmation_xpath = '//div[@class="Receipt-container--businessAndConfirmationContainer"]/p'
        confirmation_element = self.wait.until(ec.presence_of_element_located((By.XPATH, confirmation_xpath)))
        return confirmation_element.get_attribute('innerText')
