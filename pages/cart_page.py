from selenium.webdriver.common.by import By
from .base_page import BasePage


class CartPage(BasePage):
    def ready(self):
        self.path_is('/cart.html')
        return self

    def items(self):
        self.visible((By.CSS_SELECTOR, '.cart_item'))
        return [dict(name=p.find_element(By.CSS_SELECTOR, '.inventory_item_name').text,
                     price=p.find_element(By.CSS_SELECTOR, '.inventory_item_price').text)
                for p in self.driver.find_elements(By.CSS_SELECTOR, '.cart_item')]

    def checkout(self):
        self.click(self.testid('checkout'))
