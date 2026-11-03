"""All catalog products, images, detail links, sorting, and detail-page cart actions."""
import json
from decimal import Decimal
from pathlib import Path

import pytest

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

PRODUCTS = json.loads((Path(__file__).parents[1] / 'testdata/products.json').read_text())
pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-PRODUCTS')]


def test_catalog_matches_reviewable_baseline(inventory):
    actual = inventory.catalog()
    assert [{key: row[key] for key in ('name', 'price', 'description')} for row in actual] == [
        {key: row[key] for key in ('name', 'price', 'description')} for row in PRODUCTS]
    assert len({row['image_src'] for row in actual}) == len(PRODUCTS)
    for row in actual:
        assert row['image_loaded'], f"Broken image: {row['name']}"
        assert row['image_alt'] == row['name']


@pytest.mark.parametrize('order,key,reverse,label', [
    ('az', 'name', False, 'Name (A to Z)'), ('za', 'name', True, 'Name (Z to A)'),
    ('lohi', 'price', False, 'Price (low to high)'), ('hilo', 'price', True, 'Price (high to low)'),
], ids=['name-ascending', 'name-descending', 'price-ascending', 'price-descending'])
def test_sorting(inventory, order, key, reverse, label):
    # Change away from the default before testing it, so az also exercises an actual transition.
    inventory.sort('za' if order == 'az' else 'az')
    inventory.sort(order)
    rows = inventory.product_details()
    values = [Decimal(row[key].removeprefix('$')) if key == 'price' else row[key] for row in rows]
    assert values == sorted(values, reverse=reverse)
    assert sorted((row['name'], row['price']) for row in rows) == sorted(
        (row['name'], row['price']) for row in PRODUCTS)
    assert inventory.visible(inventory.testid('active-option')).text == label


def test_sorting_preserves_cart_selection(inventory, driver, base_url):
    inventory.add()
    inventory.sort('hilo')
    assert inventory.badge_count() == 1
    assert inventory.button_text('remove') == 'Remove'
    inventory.open_cart()
    assert CartPage(driver, base_url).ready().items() == [{'name': PRODUCTS[0]['name'], 'price': PRODUCTS[0]['price']}]


@pytest.mark.parametrize('product', PRODUCTS, ids=lambda product: product['slug'])
@pytest.mark.parametrize('link', ['title', 'img'])
def test_every_product_detail_link(inventory, driver, base_url, product, link):
    listing = next(row for row in inventory.catalog() if row['name'] == product['name'])
    inventory.open_product(product['id'], link)
    detail = ProductPage(driver, base_url).ready(product['id'])
    assert detail.details() == listing
    detail.back_to_products()
    assert InventoryPage(driver, base_url).ready().title() == 'Products'


@pytest.mark.parametrize('product', PRODUCTS, ids=lambda product: product['slug'])
def test_add_and_remove_from_product_details(inventory, driver, base_url, product):
    inventory.open_product(product['id'])
    detail = ProductPage(driver, base_url).ready(product['id'])
    detail.add()
    assert detail.visible(detail.testid('remove')).text == 'Remove'
    detail.open_cart()
    cart = CartPage(driver, base_url).ready()
    assert cart.items() == [{key: product[key] for key in ('name', 'price')}]
    cart.open_product(product['id'])
    detail.ready(product['id']).remove()
    assert detail.visible(detail.testid('add-to-cart')).text == 'Add to cart'
    detail.back_to_products()
    listing = InventoryPage(driver, base_url).ready()
    assert listing.badge_count() == 0
    assert listing.button_text('add-to-cart', product['slug']) == 'Add to cart'
    listing.open_cart()
    assert CartPage(driver, base_url).ready().items() == []


def test_inventory_selection_is_reflected_on_details(inventory, driver, base_url):
    inventory.add()
    inventory.open_product(4)
    detail = ProductPage(driver, base_url).ready(4)
    assert detail.badge_count() == 1
    assert detail.visible(detail.testid('remove')).text == 'Remove'
