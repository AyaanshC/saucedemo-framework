from .base_page import BasePage


class LoginPage(BasePage):
    def login(self, username, password):
        self.fill(self.testid('username'), username)
        self.fill(self.testid('password'), password)
        self.click(self.testid('login-button'))

    def ready(self):
        self.visible(self.testid('login-button'))
        return self
