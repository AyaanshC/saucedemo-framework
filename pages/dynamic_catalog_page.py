"""Dynamic catalog demos use condition-based waits instead of fixed delays."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .app_page import AppPage


class DynamicCatalogPage(AppPage):
    def open_mode(self, mode):
        self.menu_action('dynamic-catalog')
        self.click(self.testid('dynamic-catalog-' + mode + '-link'))
        return self.ready(mode)

    def ready(self, mode):
        self.path_is(f'/dynamic-catalog-{mode}.html')
        self.visible(self.testid('title'))
        return self

    def items(self, mode):
        prefix = 'lazy-load' if mode == 'lazy-load' else 'spinner'
        names = self.driver.find_elements(By.CSS_SELECTOR, f'[data-test^="{prefix}-item-"][data-test$="-name"]')
        return [dict(name=name.text, price=self.driver.find_element(
            *self.testid(name.get_attribute('data-test').removesuffix('-name') + '-price')).text)
                for name in names]

    def wait_for_spinner_results(self):
        self.wait.until(EC.invisibility_of_element_located(self.testid('dynamic-catalog-spinner')))
        self.wait.until(lambda _: len(self.items('spinner')) == 6)

    def load_more(self):
        before = len(self.items('lazy-load'))
        sentinel = self.visible(self.testid('dynamic-catalog-lazy-load-sentinel'))
        self.driver.execute_script('arguments[0].scrollIntoView({block: "center"});', sentinel)
        self.pause_for_demo()
        self.wait.until(lambda _: len(self.items('lazy-load')) > before)

    def slider_item(self):
        state = self.slider_state()
        return {key: state[key] for key in ('name', 'price')}

    def slider_state(self):
        self.visible(self.testid('dynamic-catalog-slider-item-name'))
        # One browser task captures a consistent state even when the carousel timer fires.
        return self.driver.execute_script('''
            const text = id => document.querySelector(`[data-test="${id}"]`).textContent.trim();
            return {
                name: text('dynamic-catalog-slider-item-name'),
                price: text('dynamic-catalog-slider-item-price'),
                dots: Array.from(document.querySelectorAll('[data-test^="dynamic-catalog-slider-dot-"]'))
                    .map(dot => ({label: dot.getAttribute('aria-label'), current: dot.getAttribute('aria-current')}))
            };
        ''')

    def select_slide(self, index, expected_name):
        # Observe the timer-controlled state before any presentation pause can advance it again.
        self.wait.until(EC.element_to_be_clickable(self.testid(f'dynamic-catalog-slider-dot-{index}'))).click()
        def selected(_):
            state = self.slider_state()
            return state if state['name'] == expected_name else False
        return self.wait.until(selected)
