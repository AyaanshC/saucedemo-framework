import base64
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

ROOT = Path(__file__).parent
REPORTS = Path(os.environ.get('SAUCE_DEMO_OUTPUT', ROOT / 'reports'))
log = logging.getLogger('framework')


def pytest_addoption(parser):
    parser.addoption('--headed', action='store_true', help='Show Chrome for the live demo')
    parser.addoption('--base-url', default='https://www.saucedemo.com')
    parser.addoption('--driver-path', default=os.getenv('CHROMEDRIVER_PATH'))


def pytest_configure(config):
    for folder in ['screenshots', 'logs']:
        (REPORTS / folder).mkdir(parents=True, exist_ok=True)
    config._demo_results = []
    config._demo_start = datetime.now(timezone.utc).isoformat()


@pytest.fixture(scope='session')
def driver_path(pytestconfig):
    supplied = pytestconfig.getoption('--driver-path')
    if supplied:
        return supplied
    os.environ['WDM_LOCAL'] = '1'
    return ChromeDriverManager().install()


@pytest.fixture
def driver(pytestconfig, driver_path, tmp_path):
    download_dir = tmp_path / 'downloads'
    download_dir.mkdir()
    options = webdriver.ChromeOptions()
    headed = pytestconfig.getoption('--headed')
    if not headed:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1440,1000')
    options.add_argument('--disable-search-engine-choice-screen')
    options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.password_manager_leak_detection': False,
        'download.default_directory': str(download_dir),
        'download.prompt_for_download': False,
        'plugins.always_open_pdf_externally': True,
    })
    browser = webdriver.Chrome(service=Service(driver_path), options=options)
    try:
        browser.set_page_load_timeout(45)
        browser._download_dir = download_dir
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def base_url(pytestconfig):
    return pytestconfig.getoption('--base-url')


@pytest.fixture
def login(driver, base_url):
    return LoginPage(driver, base_url).open().ready()


@pytest.fixture
def inventory(login, driver, base_url):
    login.login('standard_user', 'secret_sauce')
    return InventoryPage(driver, base_url).ready()


@pytest.fixture
def checkout(inventory, driver, base_url):
    inventory.add()
    inventory.open_cart()
    CartPage(driver, base_url).ready().checkout()
    return CheckoutPage(driver, base_url).ready()


@pytest.fixture(autouse=True)
def test_logging(request):
    log.info('TEST %s START', request.node.nodeid)
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    screenshot = None
    if report.failed and 'driver' in item.funcargs:
        try:
            browser = item.funcargs['driver']
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
            target = REPORTS / 'screenshots' / f'{safe_name}_{report.when}.png'
            screenshot = os.path.relpath(target, ROOT).replace(os.sep, '/')
            png = browser.get_screenshot_as_png()
            target.write_bytes(png)
            extras = getattr(report, 'extras', [])
            extras.append(pytest_html.extras.png(base64.b64encode(png).decode(), name='Failure screenshot'))
            extras.append(pytest_html.extras.text(browser.current_url, name='Failure URL'))
            report.extras = extras
        except Exception:
            log.exception('Screenshot capture failed')
    if report.when == 'call' or (report.when in ('setup', 'teardown') and report.failed):
        log.info('TEST %s STATUS %s (%s)', item.nodeid, report.outcome.upper(), report.when)
        item.config._demo_results.append({
            'test': item.nodeid, 'phase': report.when, 'outcome': report.outcome,
            'duration_seconds': round(report.duration, 3), 'screenshot': screenshot,
            'requirements': [m.args[0] for m in item.iter_markers('requirement')],
            'failure': str(report.longrepr) if report.failed else None,
        })


def pytest_sessionfinish(session, exitstatus):
    if session.config.option.collectonly:
        # Inspecting coverage must not replace evidence from the last executed test session.
        return
    data = {'started_utc': session.config._demo_start,
            'finished_utc': datetime.now(timezone.utc).isoformat(),
            'exit_code': int(exitstatus), 'results': session.config._demo_results}
    (REPORTS / 'run-summary.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
