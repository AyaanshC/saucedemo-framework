"""Common header/menu/footer behavior and reset across authenticated screens."""
import pytest

from pages.app_page import AppPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage

pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-NAVIGATION')]


def test_menu_opens_and_closes(inventory, driver):
    inventory.open_menu()
    for action, text in [('inventory', 'All Items'), ('dynamic-catalog', 'Dynamic Catalog'),
                         ('about', 'About'), ('logout', 'Logout'), ('reset', 'Reset App State')]:
        assert inventory.visible(inventory.testid(action + '-sidebar-link')).text == text
    assert inventory.visible(inventory.testid('about-sidebar-link')).get_attribute('href') == 'https://saucelabs.com/'
    inventory.close_menu()
    assert not driver.find_element(*inventory.testid('logout-sidebar-link')).is_displayed()
    assert inventory.title() == 'Products'


@pytest.mark.parametrize('screen', ['cart', 'details', 'information', 'overview', 'complete'])
def test_all_items_menu_from_other_screens(inventory, driver, base_url, screen):
    inventory.add()
    if screen == 'details':
        inventory.open_product(4)
        page = ProductPage(driver, base_url).ready(4)
    else:
        inventory.open_cart()
        page = CartPage(driver, base_url).ready()
        if screen in ('information', 'overview', 'complete'):
            page.checkout()
            page = CheckoutPage(driver, base_url).ready()
        if screen in ('overview', 'complete'):
            page.continue_with('Demo', 'Tester', '12345')
            page.overview_ready()
        if screen == 'complete':
            page.finish()
    page.menu_action('inventory')
    listing = InventoryPage(driver, base_url).ready()
    assert listing.title() == 'Products'
    assert listing.badge_count() == (0 if screen == 'complete' else 1)


@pytest.mark.parametrize('path', ['/inventory.html', '/cart.html'])
def test_reset_app_state_clears_persisted_cart(inventory, driver, base_url, path):
    inventory.add()
    inventory.add('sauce-labs-bike-light', expected_count=2)
    inventory.open(path)
    page = AppPage(driver, base_url)
    page.menu_action('reset')
    page.close_menu()
    # Refresh verifies persisted state; immediate button repaint is a separate UI concern.
    page.refresh()
    page.open('/inventory.html')
    listing = InventoryPage(driver, base_url).ready()
    assert listing.badge_count() == 0
    assert all(product['action'] == 'Add to cart' for product in listing.product_details())
    listing.open_cart()
    assert CartPage(driver, base_url).ready().items() == []


@pytest.mark.parametrize('path', ['/inventory.html', '/inventory-item.html?id=4', '/cart.html',
                                   '/checkout-step-one.html', '/checkout-step-two.html', '/checkout-complete.html'])
def test_footer_links_on_each_screen(inventory, driver, base_url, path):
    page = AppPage(driver, base_url).open(path)
    assert page.footer_links() == {
        'social-x': {'href': 'https://x.com/saucelabs', 'target': '_blank'},
        'social-facebook': {'href': 'https://www.facebook.com/saucelabs', 'target': '_blank'},
        'social-linkedin': {'href': 'https://www.linkedin.com/company/sauce-labs/', 'target': '_blank'},
    }
    assert 'Sauce Labs. All Rights Reserved.' in page.visible(page.testid('footer-copy')).text


@pytest.mark.parametrize('path', ['/cart.html', '/inventory-item.html?id=4', '/checkout-step-one.html', '/checkout-step-two.html'])
def test_logout_from_other_screens(inventory, driver, base_url, path):
    page = AppPage(driver, base_url).open(path)
    page.logout()
    LoginPage(driver, base_url).ready()
    assert driver.current_url.rstrip('/') == base_url.rstrip('/')
