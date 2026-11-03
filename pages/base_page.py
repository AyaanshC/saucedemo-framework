"""Shared explicit waits and observable page actions."""
import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver, base_url, timeout=12):
        self.driver = driver
        self.base_url = base_url.rstrip('/')
        self.wait = WebDriverWait(driver, timeout)

    @staticmethod
    def testid(value):
        return By.CSS_SELECTOR, f'[data-test="{value}"]'

    def pause_for_demo(self):
        """Give viewers time to follow an action; explicit waits still check readiness."""
        delay = getattr(self.driver, '_demo_step_delay', 0)
        if delay:
            time.sleep(delay)

    def open(self, path='/'):
        log.info('STEP navigate %s', path)
        self.driver.get(self.base_url + path)
        self.pause_for_demo()
        return self

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        log.info('STEP click %s', locator)
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        self.pause_for_demo()

    def fill(self, locator, value):
        # Do not log field values, which may contain credentials or personal data.
        log.info('STEP fill %s', locator)
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)
        self.pause_for_demo()

    def path_is(self, suffix):
        self.wait.until(lambda d: d.current_url.split('?')[0].endswith(suffix))

    def title(self):
        return self.visible(self.testid('title')).text

    def error(self):
        return self.visible(self.testid('error')).text
