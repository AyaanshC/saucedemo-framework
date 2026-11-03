import json
from pathlib import Path
import pytest

pytestmark = [pytest.mark.regression, pytest.mark.case_study]
CASES = json.loads((Path(__file__).parents[1] / 'testdata/postal_cases.json').read_text())


@pytest.mark.requirement('FR-11')
def test_checkout_navigation(checkout):
    assert checkout.title() == 'Checkout: Your Information'


@pytest.mark.smoke
@pytest.mark.parametrize('first,last,postal,error', [
    pytest.param('', 'Tester', '12345', 'First Name is required', marks=pytest.mark.requirement('FR-12'), id='missing-first-name'),
    pytest.param('Demo', '', '12345', 'Last Name is required', marks=pytest.mark.requirement('FR-13'), id='missing-last-name'),
    pytest.param('Demo', 'Tester', '', 'Postal Code is required', marks=pytest.mark.requirement('FR-14'), id='missing-postal'),
])
def test_mandatory_information(checkout, first, last, postal, error):
    checkout.continue_with(first, last, postal)
    assert checkout.outcome() == 'error'
    assert error in checkout.error()
    checkout.path_is('/checkout-step-one.html')


@pytest.mark.requirement('FR-14')
@pytest.mark.parametrize('case', [pytest.param(c, id=c['id'], marks=pytest.mark.smoke if c['expected'] == 'overview' else ()) for c in CASES])
def test_postal_code_contract(checkout, case):
    checkout.continue_with('Demo', 'Tester', case['postal'])
    actual = checkout.outcome()
    assert actual == case['expected'], (
        f"FR-14: postal={case['postal']!r}; expected {case['expected']}, got {actual}. "
        'If invalid input reached Overview, the AUT violates the case-study contract.'
    )
    if case['expected'] == 'error':
        assert checkout.error()
        checkout.path_is('/checkout-step-one.html')
    else:
        assert checkout.title() == 'Checkout: Overview'


@pytest.mark.requirement('FR-15')
def test_checkout_overview(checkout):
    checkout.continue_with('Demo', 'Tester', '12345')
    assert checkout.outcome() == 'overview'
    assert checkout.title() == 'Checkout: Overview'


@pytest.mark.smoke
@pytest.mark.requirement('FR-16')
def test_finish_order(checkout):
    checkout.continue_with('Demo', 'Tester', '12345')
    assert checkout.outcome() == 'overview'
    assert checkout.finish().lower() == 'thank you for your order!'
