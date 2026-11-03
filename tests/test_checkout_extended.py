"""Checkout recovery, navigation, monetary accuracy, completion, and downloads."""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

PRODUCTS = json.loads((Path(__file__).parents[1] / 'testdata/products.json').read_text())
pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-CHECKOUT')]


def test_required_field_validation_order(checkout):
    for first, last, postal, message in [
        ('', '', '', 'First Name is required'),
        ('Demo', '', '', 'Last Name is required'),
        ('Demo', 'Tester', '', 'Postal Code is required'),
    ]:
        checkout.continue_with(first, last, postal)
        assert checkout.outcome() == 'error'
        assert message in checkout.error()
        checkout.path_is('/checkout-step-one.html')


@pytest.mark.parametrize('first,last,postal', [('', 'Tester', '12345'), ('Demo', '', '12345'), ('Demo', 'Tester', '')],
                         ids=['first-name', 'last-name', 'postal'])
def test_correct_checkout_information_after_error(checkout, first, last, postal):
    checkout.continue_with(first, last, postal)
    assert checkout.outcome() == 'error'
    checkout.continue_with('Demo', 'Tester', '12345')
    assert checkout.outcome() == 'overview'
    assert checkout.title() == 'Checkout: Overview'


def test_dismiss_checkout_error_preserves_entered_values(checkout, driver):
    checkout.continue_with('', 'Tester', '12345')
    assert checkout.error()
    checkout.dismiss_error()
    assert not driver.find_elements(*checkout.testid('error'))
    assert checkout.visible(checkout.testid('lastName')).get_attribute('value') == 'Tester'
    assert checkout.visible(checkout.testid('postalCode')).get_attribute('value') == '12345'


def test_cancel_information_returns_to_cart(checkout, driver, base_url):
    checkout.fill(checkout.testid('firstName'), 'Demo')
    checkout.cancel()
    cart = CartPage(driver, base_url).ready()
    assert cart.items() == [{key: PRODUCTS[0][key] for key in ('name', 'price')}]
    assert cart.badge_count() == 1


def test_cancel_overview_returns_to_products_without_losing_cart(checkout, driver, base_url):
    checkout.continue_with('Demo', 'Tester', '12345')
    checkout.overview_ready().cancel()
    inventory = InventoryPage(driver, base_url).ready()
    assert inventory.badge_count() == 1
    assert inventory.button_text('remove') == 'Remove'
    inventory.open_cart()
    assert CartPage(driver, base_url).ready().items() == [{key: PRODUCTS[0][key] for key in ('name', 'price')}]


BASKETS = [pytest.param([product], id=product['slug']) for product in PRODUCTS] + [
    pytest.param(PRODUCTS[:2], id='two-products'), pytest.param(PRODUCTS, id='all-six-products')]


@pytest.mark.parametrize('basket', BASKETS)
def test_order_contents_totals_and_completion(inventory, driver, base_url, basket):
    for count, product in enumerate(basket, start=1):
        inventory.add(product['slug'], expected_count=count)
    inventory.open_cart()
    CartPage(driver, base_url).ready().checkout()
    checkout = CheckoutPage(driver, base_url).ready()
    checkout.continue_with('Demo', 'Tester', '12345')
    checkout.overview_ready()
    assert checkout.line_items() == [
        {**{key: product[key] for key in ('name', 'price', 'description')}, 'quantity': 1} for product in basket]
    subtotal = sum((Decimal(product['price'].removeprefix('$')) for product in basket), Decimal('0.00'))
    # App baseline: USD, 8% tax rounded to cents. This is documented separately from the case-study FRs.
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    assert checkout.totals() == {'subtotal': subtotal, 'tax': tax, 'total': subtotal + tax}
    assert checkout.visible(checkout.testid('payment-info-value')).text == 'SauceCard #31337'
    assert checkout.visible(checkout.testid('shipping-info-value')).text == 'Free Pony Express Delivery!'
    assert checkout.badge_count() == len(basket)
    assert checkout.finish() == 'Thank you for your order!'
    assert checkout.title() == 'Checkout: Complete!'
    assert 'Your order has been dispatched' in checkout.visible(checkout.testid('complete-text')).text
    image = checkout.visible(checkout.testid('pony-express'))
    checkout.wait.until(lambda _: image.get_property('complete'))
    assert image.get_property('naturalWidth') > 0
    assert checkout.badge_count() == 0
    checkout.back_home()
    inventory.ready()
    assert all(product['action'] == 'Add to cart' for product in inventory.product_details())
    inventory.open_cart()
    assert CartPage(driver, base_url).ready().items() == []


@pytest.mark.parametrize('first,last', [('Anne-Marie', "O'Neil"), ('Asha', 'Rao')],
                         ids=['hyphen-and-apostrophe', 'ordinary-names'])
def test_valid_names_can_continue(checkout, first, last):
    checkout.continue_with(first, last, '12345')
    assert checkout.outcome() == 'overview'
    assert checkout.title() == 'Checkout: Overview'


@pytest.mark.parametrize('product', PRODUCTS, ids=lambda product: product['slug'])
def test_overview_product_links(inventory, driver, base_url, product):
    inventory.add(product['slug'])
    inventory.open_cart()
    CartPage(driver, base_url).ready().checkout()
    checkout = CheckoutPage(driver, base_url).ready()
    checkout.continue_with('Demo', 'Tester', '12345')
    checkout.overview_ready().open_product(product['id'])
    detail = ProductPage(driver, base_url).ready(product['id'])
    assert detail.details()['name'] == product['name']
    assert detail.badge_count() == 1


def test_second_order_starts_with_a_clean_cart(checkout, driver, base_url):
    checkout.continue_with('Demo', 'Tester', '12345')
    checkout.finish()
    checkout.back_home()
    inventory = InventoryPage(driver, base_url).ready()
    inventory.add(PRODUCTS[1]['slug'])
    inventory.open_cart()
    CartPage(driver, base_url).ready().checkout()
    checkout.ready().continue_with('Second', 'Order', '123456')
    checkout.overview_ready()
    assert checkout.line_items() == [{**{key: PRODUCTS[1][key] for key in ('name', 'price', 'description')}, 'quantity': 1}]
    assert checkout.totals() == {'subtotal': Decimal('9.99'), 'tax': Decimal('0.80'), 'total': Decimal('10.79')}
    assert checkout.finish() == 'Thank you for your order!'


def test_generate_pdf_order_download(checkout, driver):
    checkout.continue_with('Demo', 'Tester', '12345')
    checkout.finish()
    checkout.generate_pdf()
    folder = driver._download_dir

    def finished_download(_):
        files = list(folder.glob('*.pdf'))
        return files if files and not list(folder.glob('*.crdownload')) else False

    files = checkout.wait.until(finished_download)
    assert len(files) == 1
    content = files[0].read_bytes()
    assert content.startswith(b'%PDF-'), f'Not a PDF: {files[0].name}'
    assert content.rstrip().endswith(b'%%EOF'), 'PDF download is incomplete'
    assert len(content) > 1000
    assert checkout.title() == 'Checkout: Complete!'


@pytest.mark.proposed_contract
def test_empty_cart_cannot_start_checkout(inventory, driver, base_url):
    inventory.open_cart()
    cart = CartPage(driver, base_url).ready()
    button = cart.visible(cart.testid('checkout'))
    if button.is_enabled():
        cart.checkout()
    assert driver.current_url.split('?')[0].endswith('/cart.html'), 'Empty cart was allowed to enter checkout'


@pytest.mark.parametrize('field', [
    pytest.param('firstName', marks=pytest.mark.proposed_contract),
    pytest.param('lastName', marks=pytest.mark.proposed_contract),
    pytest.param('postalCode', marks=pytest.mark.requirement('FR-14')),
])
def test_whitespace_only_required_field_is_rejected(checkout, field):
    values = {'firstName': 'Demo', 'lastName': 'Tester', 'postalCode': '12345'}
    values[field] = '   '
    checkout.continue_with(values['firstName'], values['lastName'], values['postalCode'])
    assert checkout.outcome() == 'error', f'{field} accepted whitespace-only input'
    assert checkout.error()
    checkout.path_is('/checkout-step-one.html')
