from selenium.webdriver.common.by import By
from .app_page import AppPage


class ProductPage(AppPage):
    def ready(self, product_id):
        self.path_is('/inventory-item.html')
        self.wait.until(lambda d: f'id={product_id}' in d.current_url.split('#')[0].split('?')[-1].split('&'))
        self.visible(self.testid('inventory-item-name'))
        return self

    def details(self):
        image = self.visible((By.CSS_SELECTOR, '.inventory_details_img'))
        self.wait.until(lambda _: image.get_property('complete'))
        return dict(name=self.visible(self.testid('inventory-item-name')).text,
                    price=self.visible(self.testid('inventory-item-price')).text,
                    description=self.visible(self.testid('inventory-item-desc')).text,
                    image_src=image.get_attribute('src'), image_alt=image.get_attribute('alt'),
                    image_loaded=image.get_property('naturalWidth') > 0)

    def add(self, expected_count=1):
        self.click(self.testid('add-to-cart'))
        self.wait.until(lambda _: self.badge_count() == expected_count)

    def remove(self, expected_count=0):
        self.click(self.testid('remove'))
        self.wait.until(lambda _: self.badge_count() == expected_count)

    def back_to_products(self):
        self.click(self.testid('back-to-products'))
