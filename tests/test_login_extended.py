"""Authentication, error recovery, keyboard submission, and session boundaries."""
import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.regression, pytest.mark.extended, pytest.mark.requirement('APP-AUTH')]


@pytest.mark.parametrize('username,password,error', [
    pytest.param('locked_out_user', 'secret_sauce', 'Sorry, this user has been locked out', id='locked-account'),
    pytest.param('unknown_user', 'secret_sauce', 'Username and password do not match', id='unknown-account'),
    pytest.param('STANDARD_USER', 'secret_sauce', 'Username and password do not match', id='username-case'),
    pytest.param('standard_user', 'SECRET_SAUCE', 'Username and password do not match', id='password-case'),
    pytest.param(' standard_user ', 'secret_sauce', 'Username and password do not match', id='username-spaces'),
    pytest.param('standard_user', ' secret_sauce ', 'Username and password do not match', id='password-spaces'),
])
def test_additional_rejected_credentials(login, driver, username, password, error):
    login.login(username, password)
    assert error in login.error()
    assert '/inventory.html' not in driver.current_url
    login.ready()


@pytest.mark.parametrize('username', ['problem_user', 'performance_glitch_user', 'error_user', 'visual_user'])
def test_other_advertised_accounts_can_authenticate(login, driver, base_url, username):
    # Only authentication is checked; these personas deliberately contain downstream defects.
    login.login(username, 'secret_sauce')
    assert InventoryPage(driver, base_url).ready().title() == 'Products'


def test_password_input_is_masked(login):
    field = login.visible(login.testid('password'))
    assert field.get_attribute('type') == 'password'
    login.fill(login.testid('password'), 'secret_sauce')
    assert field.get_attribute('value') == 'secret_sauce'


def test_login_with_enter_key(login, driver, base_url):
    login.submit_with_enter('standard_user', 'secret_sauce')
    assert InventoryPage(driver, base_url).ready().title() == 'Products'


def test_dismiss_login_error(login, driver):
    login.login('standard_user', 'wrong_password')
    assert login.error()
    login.dismiss_error()
    assert not driver.find_elements(*login.testid('error'))
    assert not driver.find_elements('css selector', '.error_icon')
    login.ready()


@pytest.mark.parametrize('username,password', [('standard_user', 'wrong_password'), ('', '')],
                         ids=['incorrect-password', 'required-fields'])
def test_correct_credentials_after_rejection(login, driver, base_url, username, password):
    login.login(username, password)
    assert login.error()
    login.login('standard_user', 'secret_sauce')
    assert InventoryPage(driver, base_url).ready().title() == 'Products'
    assert not driver.find_elements(*login.testid('error'))


@pytest.mark.parametrize('path', ['/inventory.html', '/cart.html', '/inventory-item.html?id=4',
                                   '/checkout-step-one.html', '/checkout-step-two.html', '/checkout-complete.html'])
def test_protected_pages_in_fresh_session(login, driver, base_url, path):
    login.open(path).ready()
    assert driver.current_url.rstrip('/') == base_url.rstrip('/')
    assert 'You can only access' in login.error()


def test_logout_then_login_again(inventory, driver, base_url):
    inventory.logout()
    login = LoginPage(driver, base_url).ready()
    login.login('standard_user', 'secret_sauce')
    assert InventoryPage(driver, base_url).ready().title() == 'Products'
