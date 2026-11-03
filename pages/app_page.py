"""Shared authenticated navigation and cart/summary readers."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class AppPage(BasePage):
    def badge_count(self):
        badges = self.driver.find_elements(*self.testid('shopping-cart-badge'))
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        self.click(self.testid('shopping-cart-link'))

    def open_menu(self):
        self.click((By.ID, 'react-burger-menu-btn'))
        self.visible(self.testid('logout-sidebar-link'))

    def close_menu(self):
        self.click((By.ID, 'react-burger-cross-btn'))
        self.wait.until(EC.invisibility_of_element_located(self.testid('logout-sidebar-link')))

    def menu_action(self, action):
        self.open_menu()
        self.click(self.testid(action + '-sidebar-link'))

    def logout(self):
        self.menu_action('logout')

    def line_items(self):
        self.visible(self.testid('cart-list'))
        return [dict(name=row.find_element(*self.testid('inventory-item-name')).text,
                     price=row.find_element(*self.testid('inventory-item-price')).text,
                     description=row.find_element(*self.testid('inventory-item-desc')).text,
                     quantity=int(row.find_element(*self.testid('item-quantity')).text))
                for row in self.driver.find_elements(By.CSS_SELECTOR, '.cart_item')]

    def open_product(self, product_id, link='title'):
        self.click(self.testid(f'item-{product_id}-{link}-link'))

    def footer_links(self):
        self.visible(self.testid('footer'))
        return {link.get_attribute('data-test'): dict(href=link.get_attribute('href'),
                                                     target=link.get_attribute('target'))
                for link in self.driver.find_elements(By.CSS_SELECTOR, 'footer a')}

    def refresh(self):
        self.driver.refresh()
        self.pause_for_demo()
