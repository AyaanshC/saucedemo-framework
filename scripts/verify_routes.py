"""Record HTTP routes and prove the Products SPA bootstrap URL using real Chrome."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

BASE_URL = 'https://www.saucedemo.com'
PRODUCTS_DOCUMENT = '/?/inventory.html'


def verify_routes(driver_path=None):
    evidence = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'http': []}
    for path in ['/', '/inventory.html', PRODUCTS_DOCUMENT]:
        response = requests.get(BASE_URL + path, timeout=30)
        evidence['http'].append(dict(requested_url=BASE_URL + path, final_url=response.url,
                                    status=response.status_code, has_app_root='id="root"' in response.text,
                                    is_spa_redirect='<title>Single Page Apps for GitHub Pages</title>' in response.text))
        if path == '/inventory.html':
            evidence['redirect_document'] = response.text
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1440,1000')
    options.add_experimental_option('prefs', {'credentials_enable_service': False,
                                            'profile.password_manager_enabled': False,
                                            'profile.password_manager_leak_detection': False})
    if not driver_path:
        import os
        os.environ['WDM_LOCAL'] = '1'
        driver_path = ChromeDriverManager().install()
    browser = webdriver.Chrome(service=Service(str(driver_path)), options=options)
    try:
        LoginPage(browser, BASE_URL).open().ready().login('standard_user', 'secret_sauce')
        products = InventoryPage(browser, BASE_URL).ready()
        evidence['browser_version'] = browser.capabilities['browserVersion']
        for name, path in [('browser_direct_route', '/inventory.html'),
                           ('browser_bootstrap_route', PRODUCTS_DOCUMENT)]:
            browser.get(BASE_URL + path)
            products.ready()
            evidence[name] = dict(displayed_url=browser.current_url, title=products.title(),
                                  products=len(products.products()), navigation=browser.execute_script('''
                return performance.getEntriesByType('navigation').map(e =>
                    ({name:e.name, responseStatus:e.responseStatus, duration:e.duration}));
            '''))
    finally:
        browser.quit()
    evidence['verified'] = all([
        evidence['http'][0]['status'] == 200,
        evidence['http'][2]['status'] == 200,
        evidence['http'][2]['has_app_root'],
        all(evidence[name]['title'] == 'Products' and evidence[name]['products'] >= 6
            and evidence[name]['displayed_url'] == BASE_URL + '/inventory.html'
            and evidence[name]['navigation'][0]['name'] == BASE_URL + PRODUCTS_DOCUMENT
            and evidence[name]['navigation'][0]['responseStatus'] == 200
            for name in ['browser_direct_route', 'browser_bootstrap_route']),
    ])
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--driver-path')
    args = parser.parse_args()
    result = verify_routes(args.driver_path)
    output = ROOT / 'performance/route-evidence.json'
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"Route verified: {result['verified']}. Evidence: {output}")
    sys.exit(0 if result['verified'] else 1)
