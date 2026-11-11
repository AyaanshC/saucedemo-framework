from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .app_page import AppPage


class InventoryPage(AppPage):
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

    def sort(self, value):
        Select(self.visible(self.testid('product-sort-container'))).select_by_value(value)
        self.wait.until(lambda _: self.sort_value() == value)

    def sort_value(self):
        return Select(self.visible(self.testid('product-sort-container'))).first_selected_option.get_attribute('value')

    def catalog(self):
        entries = []
        for row in self.products():
            image = row.find_element(By.TAG_NAME, 'img')
            self.wait.until(lambda _: image.get_property('complete'))
            entries.append(dict(name=row.find_element(*self.testid('inventory-item-name')).text,
                                price=row.find_element(*self.testid('inventory-item-price')).text,
                                description=row.find_element(*self.testid('inventory-item-desc')).text,
                                image_src=image.get_attribute('src'), image_alt=image.get_attribute('alt'),
                                image_loaded=image.get_property('naturalWidth') > 0))
        return entries
