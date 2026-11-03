from .app_page import AppPage


class CartPage(AppPage):
    def ready(self):
        self.path_is('/cart.html')
        self.visible(self.testid('cart-list'))
        return self

    def items(self):
        return [{key: item[key] for key in ('name', 'price')} for item in self.line_items()]

    def checkout(self):
        self.click(self.testid('checkout'))

    def remove(self, slug, expected_count):
        self.click(self.testid('remove-' + slug))
        self.wait.until(lambda _: len(self.line_items()) == expected_count)

    def continue_shopping(self):
        self.click(self.testid('continue-shopping'))
