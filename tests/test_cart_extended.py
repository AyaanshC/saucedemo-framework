"""Empty/multi-item carts, removal, persistence, and product navigation."""
import json
from pathlib import Path

import pytest

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

PRODUCTS = json.loads((Path(__file__).parents[1] / 'testdata/products.json').read_text())
pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-CART')]


def test_empty_cart(inventory, driver, base_url):
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    assert cart.title() == 'Your Cart'
    assert cart.items() == []
    assert cart.badge_count() == 0
    assert not driver.find_elements('css selector', '.cart_item button')


@pytest.mark.parametrize('populated', [False, True], ids=['empty', 'with-product'])
def test_continue_shopping(inventory, driver, base_url, populated):
    if populated:
        inventory.add()
    inventory.open_cart()
    CartPage(driver, base_url).ready().continue_shopping()
    listing = InventoryPage(driver, base_url).ready()
    assert listing.title() == 'Products'
    assert listing.badge_count() == int(populated)
    assert listing.button_text('remove' if populated else 'add-to-cart') == ('Remove' if populated else 'Add to cart')


@pytest.mark.parametrize('product', PRODUCTS, ids=lambda product: product['slug'])
def test_remove_each_product_inside_cart(inventory, driver, base_url, product):
    inventory.add(product['slug'])
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    cart.remove(product['slug'], expected_count=0)
    assert cart.items() == []
    assert cart.badge_count() == 0
    cart.continue_shopping()
    listing = InventoryPage(driver, base_url).ready()
    assert listing.button_text('add-to-cart', product['slug']) == 'Add to cart'


def test_removing_one_product_preserves_the_other(inventory, driver, base_url):
    inventory.add()
    inventory.add(PRODUCTS[1]['slug'], expected_count=2)
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    cart.remove(PRODUCTS[0]['slug'], expected_count=1)
    assert cart.badge_count() == 1
    assert cart.items() == [{key: PRODUCTS[1][key] for key in ('name', 'price')}]


def test_all_products_can_be_added_together(inventory, driver, base_url):
    for count, product in enumerate(PRODUCTS, start=1):
        inventory.add(product['slug'], expected_count=count)
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    rows = cart.line_items()
    assert rows == [{**{key: product[key] for key in ('name', 'price', 'description')}, 'quantity': 1}
                    for product in PRODUCTS]
    assert cart.badge_count() == len(PRODUCTS)


@pytest.mark.parametrize('path', ['/inventory.html', '/cart.html'])
def test_cart_survives_refresh(inventory, driver, base_url, path):
    inventory.add()
    inventory.add(PRODUCTS[1]['slug'], expected_count=2)
    inventory.open(path).refresh()
    if path == '/inventory.html':
        inventory.ready()
        assert inventory.button_text('remove') == 'Remove'
        inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    assert cart.badge_count() == 2
    assert cart.items() == [{key: product[key] for key in ('name', 'price')} for product in PRODUCTS[:2]]


def test_removed_product_can_be_added_again_without_duplicates(inventory, driver, base_url):
    inventory.add()
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    cart.remove(PRODUCTS[0]['slug'], expected_count=0)
    cart.continue_shopping()
    inventory.ready().add()
    inventory.open_cart()
    assert cart.ready().items() == [{key: PRODUCTS[0][key] for key in ('name', 'price')}]
    assert cart.badge_count() == 1


@pytest.mark.parametrize('product', PRODUCTS, ids=lambda product: product['slug'])
def test_cart_product_links(inventory, driver, base_url, product):
    inventory.add(product['slug'])
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    cart.open_product(product['id'])
    detail = ProductPage(driver, base_url).ready(product['id'])
    actual = detail.details()
    assert {key: actual[key] for key in ('name', 'price', 'description')} == {
        key: product[key] for key in ('name', 'price', 'description')}
    assert detail.badge_count() == 1
