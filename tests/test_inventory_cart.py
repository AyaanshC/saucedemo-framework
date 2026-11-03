import pytest
from pages.cart_page import CartPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.regression, pytest.mark.case_study]


@pytest.mark.requirement('FR-06')
def test_product_catalog(inventory):
    products = inventory.product_details()
    assert len(products) >= 6
    for product in products:
        assert product['name']
        assert float(product['price'].removeprefix('$')) > 0
        assert product['action'] == 'Add to cart'


@pytest.mark.smoke
@pytest.mark.requirement('FR-07')
def test_add_to_cart(inventory):
    assert inventory.badge_count() == 0
    inventory.add(expected_count=1)
    assert inventory.button_text('remove') == 'Remove'
    inventory.add('sauce-labs-bike-light', expected_count=2)
    assert inventory.badge_count() == 2
    assert inventory.button_text('remove', 'sauce-labs-bike-light') == 'Remove'


@pytest.mark.requirement('FR-08')
def test_remove_from_cart(inventory):
    inventory.add()
    inventory.add('sauce-labs-bike-light', expected_count=2)
    inventory.remove(expected_count=1)
    assert inventory.button_text('add-to-cart') == 'Add to cart'
    inventory.remove('sauce-labs-bike-light', expected_count=0)
    assert inventory.badge_count() == 0
    assert inventory.button_text('add-to-cart', 'sauce-labs-bike-light') == 'Add to cart'


@pytest.mark.requirement('FR-09')
def test_cart_details_match_products(inventory, driver, base_url):
    expected = [{k: p[k] for k in ('name', 'price')}
                for p in inventory.product_details() if p['name'] in ('Sauce Labs Backpack', 'Sauce Labs Bike Light')]
    assert len(expected) == 2
    inventory.add()
    inventory.add('sauce-labs-bike-light', expected_count=2)
    inventory.open_cart()
    assert CartPage(driver, base_url).ready().items() == expected


@pytest.mark.requirement('FR-10')
@pytest.mark.parametrize('path', ['/inventory.html', '/cart.html'])
def test_protected_page_after_logout(inventory, driver, base_url, path):
    inventory.logout()
    LoginPage(driver, base_url).ready().open(path).ready()
    assert driver.current_url.rstrip('/') == base_url.rstrip('/')
