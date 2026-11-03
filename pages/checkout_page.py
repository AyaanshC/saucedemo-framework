from .base_page import BasePage


class CheckoutPage(BasePage):
    def ready(self):
        self.path_is('/checkout-step-one.html')
        self.visible(self.testid('firstName'))
        return self

    def continue_with(self, first, last, postal):
        self.fill(self.testid('firstName'), first)
        self.fill(self.testid('lastName'), last)
        self.fill(self.testid('postalCode'), postal)
        self.click(self.testid('continue'))

    def outcome(self):
        def result(driver):
            if driver.current_url.endswith('/checkout-step-two.html'):
                return 'overview'
            errors = driver.find_elements(*self.testid('error'))
            if errors and errors[0].is_displayed():
                return 'error'
            return False
        return self.wait.until(result)

    def finish(self):
        self.path_is('/checkout-step-two.html')
        self.click(self.testid('finish'))
        self.path_is('/checkout-complete.html')
        return self.visible(self.testid('complete-header')).text
