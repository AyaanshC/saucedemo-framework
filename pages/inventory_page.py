from selenium.webdriver.common.by import By
from .base_page import BasePage


class InventoryPage(BasePage):
    def ready(self):
        self.path_is('/inventory.html')
        self.visible(self.testid('inventory-container'))
        return self

    def products(self):
        self.visible((By.CSS_SELECTOR, '.inventory_item'))
        return self.driver.find_elements(By.CSS_SELECTOR, '.inventory_item')

    def product_details(self):
        return [dict(name=p.find_element(By.CSS_SELECTOR, '.inventory_item_name').text,
                     price=p.find_element(By.CSS_SELECTOR, '.inventory_item_price').text,
                     action=p.find_element(By.TAG_NAME, 'button').text)
                for p in self.products()]

    def add(self, slug='sauce-labs-backpack', expected_count=1):
        self.click(self.testid('add-to-cart-' + slug))
        self.wait.until(lambda _: self.badge_count() == expected_count)

    def remove(self, slug='sauce-labs-backpack', expected_count=0):
        self.click(self.testid('remove-' + slug))
        self.wait.until(lambda _: self.badge_count() == expected_count)

    def button_text(self, action, slug='sauce-labs-backpack'):
        return self.visible(self.testid(action + '-' + slug)).text

    def badge_count(self):
        badges = self.driver.find_elements(By.CSS_SELECTOR, '.shopping_cart_badge')
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        self.click((By.CSS_SELECTOR, '.shopping_cart_link'))

    def logout(self):
        self.click((By.ID, 'react-burger-menu-btn'))
        self.click(self.testid('logout-sidebar-link'))
