"""Lazy loading, asynchronous spinner results, and carousel controls."""
import json
from pathlib import Path
import re

import pytest

from pages.cart_page import CartPage
from pages.dynamic_catalog_page import DynamicCatalogPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

PRODUCTS = json.loads((Path(__file__).parents[1] / 'testdata/products.json').read_text())
MODES = ['lazy-load', 'spinner', 'slider']
pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-DYNAMIC')]


def test_dynamic_submenu_expands_and_collapses(inventory, driver):
    inventory.menu_action('dynamic-catalog')
    for mode in MODES:
        assert inventory.visible(inventory.testid(f'dynamic-catalog-{mode}-link')).text
    inventory.click(inventory.testid('dynamic-catalog-sidebar-link'))
    inventory.wait.until(lambda d: all(not element.is_displayed() for mode in MODES
                         for element in d.find_elements(*inventory.testid(f'dynamic-catalog-{mode}-link'))))
    inventory.close_menu()
    assert inventory.title() == 'Products'


def test_lazy_loading_appends_products_without_losing_previous_rows(inventory, driver, base_url):
    page = DynamicCatalogPage(driver, base_url).open_mode('lazy-load')
    assert page.title() == 'Dynamic Catalog - Lazy Load'
    page.wait.until(lambda _: len(page.items('lazy-load')) > 0)
    original = page.items('lazy-load')
    page.load_more()
    expanded = page.items('lazy-load')
    assert len(expanded) > len(original)
    assert expanded[:len(original)] == original
    page.load_more()
    final = page.items('lazy-load')
    assert final[:len(expanded)] == expanded
    # This demo intentionally repeats products and sizes; uniqueness is not assumed.
    expected_prices = {product['name']: product['price'] for product in PRODUCTS}
    for row in final:
        base_name = re.sub(r' \((?:XS|S|M|L|XL|XXL)\)$', '', row['name'])
        assert base_name in expected_prices
        assert row['price'] == expected_prices[base_name]


def test_spinner_resolves_to_the_six_products(inventory, driver, base_url):
    page = DynamicCatalogPage(driver, base_url).open_mode('spinner')
    assert page.title() == 'Dynamic Catalog - Spinner'
    page.wait_for_spinner_results()
    assert page.items('spinner') == [{key: product[key] for key in ('name', 'price')}
                                     for product in sorted(PRODUCTS, key=lambda product: product['id'])]
    assert not driver.find_elements(*page.testid('dynamic-catalog-spinner'))


def test_spinner_reloads_successfully(inventory, driver, base_url):
    page = DynamicCatalogPage(driver, base_url).open_mode('spinner')
    page.wait_for_spinner_results()
    before = page.items('spinner')
    page.refresh()
    page.ready('spinner').wait_for_spinner_results()
    assert page.items('spinner') == before


def test_every_slider_dot_selects_the_correct_product(inventory, driver, base_url):
    page = DynamicCatalogPage(driver, base_url).open_mode('slider')
    assert page.title() == 'Dynamic Catalog - Slider'
    for index, product in enumerate(sorted(PRODUCTS, key=lambda product: product['id'])):
        state = page.select_slide(index, product['name'])
        assert {key: state[key] for key in ('name', 'price')} == {key: product[key] for key in ('name', 'price')}
        assert state['dots'][index] == {'label': 'Show ' + product['name'], 'current': 'true'}
        assert sum(dot['current'] == 'true' for dot in state['dots']) == 1
        page.pause_for_demo()


def test_slider_advances_automatically(inventory, driver, base_url):
    page = DynamicCatalogPage(driver, base_url).open_mode('slider')
    initial = page.slider_item()
    page.wait.until(lambda _: page.slider_item() != initial)
    assert page.slider_item() in [{key: product[key] for key in ('name', 'price')} for product in PRODUCTS]


@pytest.mark.parametrize('mode', MODES)
def test_dynamic_pages_preserve_cart_and_return_to_inventory(inventory, driver, base_url, mode):
    inventory.add()
    page = DynamicCatalogPage(driver, base_url).open_mode(mode)
    assert page.badge_count() == 1
    page.menu_action('inventory')
    inventory = InventoryPage(driver, base_url).ready()
    assert inventory.button_text('remove') == 'Remove'
    inventory.open_cart()
    assert CartPage(driver, base_url).ready().items() == [{key: PRODUCTS[0][key] for key in ('name', 'price')}]


@pytest.mark.parametrize('mode', MODES)
def test_dynamic_page_cart_shortcut(inventory, driver, base_url, mode):
    page = DynamicCatalogPage(driver, base_url).open_mode(mode)
    page.open_cart()
    cart = CartPage(driver, base_url).ready()
    assert cart.title() == 'Your Cart'
    assert cart.items() == []


@pytest.mark.parametrize('mode', MODES)
def test_dynamic_page_logout(inventory, driver, base_url, mode):
    page = DynamicCatalogPage(driver, base_url).open_mode(mode)
    page.logout()
    LoginPage(driver, base_url).ready()
    assert driver.current_url.rstrip('/') == base_url.rstrip('/')


@pytest.mark.parametrize('mode', MODES)
def test_dynamic_pages_require_authentication(login, driver, base_url, mode):
    login.open(f'/dynamic-catalog-{mode}.html').ready()
    assert driver.current_url.rstrip('/') == base_url.rstrip('/')
    assert 'You can only access' in login.error()
