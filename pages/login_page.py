from .base_page import BasePage
from selenium.webdriver.common.keys import Keys


class LoginPage(BasePage):
    def login(self, username, password):
        self.fill(self.testid('username'), username)
        self.fill(self.testid('password'), password)
        self.click(self.testid('login-button'))

    def ready(self):
        self.visible(self.testid('login-button'))
        return self

    def dismiss_error(self):
        self.click(self.testid('error-button'))
        self.wait.until(lambda d: not d.find_elements(*self.testid('error')))

    def submit_with_enter(self, username, password):
        self.fill(self.testid('username'), username)
        self.fill(self.testid('password'), password)
        self.visible(self.testid('password')).send_keys(Keys.ENTER)
