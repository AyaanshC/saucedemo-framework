import json
from pathlib import Path
import pytest
from pages.inventory_page import InventoryPage

pytestmark = pytest.mark.regression
CASES = json.loads((Path(__file__).parents[1] / 'testdata/login_cases.json').read_text())


@pytest.mark.smoke
@pytest.mark.requirement('FR-01')
def test_successful_login(login, driver, base_url):
    login.login('standard_user', 'secret_sauce')
    assert InventoryPage(driver, base_url).ready().title() == 'Products'


@pytest.mark.smoke
@pytest.mark.parametrize('case', [pytest.param(c, id=c['id'], marks=pytest.mark.requirement(c['requirement'])) for c in CASES])
def test_rejected_login(login, driver, case):
    login.login(case['username'], case['password'])
    assert case['error'] in login.error()
    assert '/inventory.html' not in driver.current_url
    login.ready()


@pytest.mark.requirement('FR-05')
@pytest.mark.parametrize('length', [29, 30, 31], ids=['below-30', 'at-30', 'above-30'])
def test_username_length_boundary(login, length):
    # All values are unknown accounts; rejection does NOT prove a length validator.
    login.login('u' * length, 'secret_sauce')
    assert 'Username and password do not match' in login.error()
    login.ready()
