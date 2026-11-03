# Expanded functional test inventory

The suite contains **157 cases: 25 original + 132 extended**. The 12-case smoke subset is unchanged.

This inventory lists the actual collected pytest node IDs. Every parameterized row is an independent case with a fresh Chrome session. All cases carry the regression marker; new modules also carry extended.

## Coverage by module

| Module | Cases | Purpose |
|---|---:|---|
| [test_cart_extended.py](../tests/test_cart_extended.py) | 20 | Empty/filled continue-shopping, remove all six product types, preserve other items, all-six quantities, refresh persistence, re-add, all product links. |
| [test_checkout.py](../tests/test_checkout.py) | 11 | Original required-field/postal validation, overview, completion (FR-11–FR-16). |
| [test_checkout_extended.py](../tests/test_checkout_extended.py) | 29 | Validation order/correction/dismissal, both cancels, eight baskets with 8% tax/total/completion, names, overview links, second order, PDF integrity, whitespace postal FR-14 and three proposed contracts. |
| [test_dynamic_catalog.py](../tests/test_dynamic_catalog.py) | 18 | Submenu, lazy append/retention/prices, spinner completion/reload, all slider dots and auto-advance, cart preservation/shortcuts, logout, fresh-session protection for all three modes. |
| [test_inventory_cart.py](../tests/test_inventory_cart.py) | 6 | Original inventory/cart and post-logout protection (FR-06–FR-10). |
| [test_login.py](../tests/test_login.py) | 8 | Original login and username-length checks (FR-01–FR-05). |
| [test_login_extended.py](../tests/test_login_extended.py) | 22 | Locked/unknown/case/space credentials, advertised accounts, masking, Enter, error dismissal/recovery, fresh-session route protection, re-login. |
| [test_navigation.py](../tests/test_navigation.py) | 18 | Open/close menu, About href, All Items from five screens, persisted reset from inventory/cart, footer destinations on six screens, logout from four screens. |
| [test_products.py](../tests/test_products.py) | 25 | Fixed six-product baseline and loaded images; four sorts; retained selections; title/image detail links and add/remove for every product. |

## Test oracles and limits

- The original 25 cases follow the case-study FR mapping in TEST_DESIGN.md; FR-05 retains its documented observability limitation.
- APP-* labels are app-area labels, not original brief IDs. The six-product JSON file, 8% tax, payment/shipping strings and link targets are observed regression baselines from 3 November 2026. Review them when intentional app changes occur.
- Three proposed_contract cases require product-owner agreement: reject empty-cart checkout and whitespace-only first/last names. Whitespace postal rejection maps directly to FR-14. All are included in the default run and can be selected separately.
- All advertised non-locked account types are checked for login. Full shopping flows use standard_user; deliberate defects in other personas are not exhaustively mapped.
- Footer and About hrefs are asserted; third-party websites are not visited. Reset checks persisted state after refresh, not immediate button repaint.
- The PDF check verifies a completed download with a PDF header, EOF marker and nontrivial size; it does not validate receipt text or pagination.
- Lazy loading is a repeating variant feed. Tests verify growth, retention and name/price relationships, without assuming uniqueness or a final page.
- This suite does not establish complete browser/device, accessibility, backend/security, or rendered performance coverage.

## Running selected coverage

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m extended
.\.venv\Scripts\python.exe -m pytest -m "not extended"
.\.venv\Scripts\python.exe -m pytest -m case_study
.\.venv\Scripts\python.exe -m pytest -m proposed_contract
.\.venv\Scripts\python.exe -m pytest -m "not proposed_contract"
```

## Individual cases

### test_cart_extended.py

- `test_empty_cart`
- `test_continue_shopping[empty]`
- `test_continue_shopping[with-product]`
- `test_remove_each_product_inside_cart[sauce-labs-backpack]`
- `test_remove_each_product_inside_cart[sauce-labs-bike-light]`
- `test_remove_each_product_inside_cart[sauce-labs-bolt-t-shirt]`
- `test_remove_each_product_inside_cart[sauce-labs-fleece-jacket]`
- `test_remove_each_product_inside_cart[sauce-labs-onesie]`
- `test_remove_each_product_inside_cart[test.allthethings()-t-shirt-(red)]`
- `test_removing_one_product_preserves_the_other`
- `test_all_products_can_be_added_together`
- `test_cart_survives_refresh[/inventory.html]`
- `test_cart_survives_refresh[/cart.html]`
- `test_removed_product_can_be_added_again_without_duplicates`
- `test_cart_product_links[sauce-labs-backpack]`
- `test_cart_product_links[sauce-labs-bike-light]`
- `test_cart_product_links[sauce-labs-bolt-t-shirt]`
- `test_cart_product_links[sauce-labs-fleece-jacket]`
- `test_cart_product_links[sauce-labs-onesie]`
- `test_cart_product_links[test.allthethings()-t-shirt-(red)]`

### test_checkout.py

- `test_checkout_navigation`
- `test_mandatory_information[missing-first-name]`
- `test_mandatory_information[missing-last-name]`
- `test_mandatory_information[missing-postal]`
- `test_postal_code_contract[four-digits-invalid]`
- `test_postal_code_contract[five-digits-valid]`
- `test_postal_code_contract[six-digits-valid]`
- `test_postal_code_contract[alphabetic-invalid]`
- `test_postal_code_contract[mixed-invalid]`
- `test_checkout_overview`
- `test_finish_order`

### test_checkout_extended.py

- `test_required_field_validation_order`
- `test_correct_checkout_information_after_error[first-name]`
- `test_correct_checkout_information_after_error[last-name]`
- `test_correct_checkout_information_after_error[postal]`
- `test_dismiss_checkout_error_preserves_entered_values`
- `test_cancel_information_returns_to_cart`
- `test_cancel_overview_returns_to_products_without_losing_cart`
- `test_order_contents_totals_and_completion[sauce-labs-backpack]`
- `test_order_contents_totals_and_completion[sauce-labs-bike-light]`
- `test_order_contents_totals_and_completion[sauce-labs-bolt-t-shirt]`
- `test_order_contents_totals_and_completion[sauce-labs-fleece-jacket]`
- `test_order_contents_totals_and_completion[sauce-labs-onesie]`
- `test_order_contents_totals_and_completion[test.allthethings()-t-shirt-(red)]`
- `test_order_contents_totals_and_completion[two-products]`
- `test_order_contents_totals_and_completion[all-six-products]`
- `test_valid_names_can_continue[hyphen-and-apostrophe]`
- `test_valid_names_can_continue[ordinary-names]`
- `test_overview_product_links[sauce-labs-backpack]`
- `test_overview_product_links[sauce-labs-bike-light]`
- `test_overview_product_links[sauce-labs-bolt-t-shirt]`
- `test_overview_product_links[sauce-labs-fleece-jacket]`
- `test_overview_product_links[sauce-labs-onesie]`
- `test_overview_product_links[test.allthethings()-t-shirt-(red)]`
- `test_second_order_starts_with_a_clean_cart`
- `test_generate_pdf_order_download`
- `test_empty_cart_cannot_start_checkout`
- `test_whitespace_only_required_field_is_rejected[firstName]`
- `test_whitespace_only_required_field_is_rejected[lastName]`
- `test_whitespace_only_required_field_is_rejected[postalCode]`

### test_dynamic_catalog.py

- `test_dynamic_submenu_expands_and_collapses`
- `test_lazy_loading_appends_products_without_losing_previous_rows`
- `test_spinner_resolves_to_the_six_products`
- `test_spinner_reloads_successfully`
- `test_every_slider_dot_selects_the_correct_product`
- `test_slider_advances_automatically`
- `test_dynamic_pages_preserve_cart_and_return_to_inventory[lazy-load]`
- `test_dynamic_pages_preserve_cart_and_return_to_inventory[spinner]`
- `test_dynamic_pages_preserve_cart_and_return_to_inventory[slider]`
- `test_dynamic_page_cart_shortcut[lazy-load]`
- `test_dynamic_page_cart_shortcut[spinner]`
- `test_dynamic_page_cart_shortcut[slider]`
- `test_dynamic_page_logout[lazy-load]`
- `test_dynamic_page_logout[spinner]`
- `test_dynamic_page_logout[slider]`
- `test_dynamic_pages_require_authentication[lazy-load]`
- `test_dynamic_pages_require_authentication[spinner]`
- `test_dynamic_pages_require_authentication[slider]`

### test_inventory_cart.py

- `test_product_catalog`
- `test_add_to_cart`
- `test_remove_from_cart`
- `test_cart_details_match_products`
- `test_protected_page_after_logout[/inventory.html]`
- `test_protected_page_after_logout[/cart.html]`

### test_login.py

- `test_successful_login`
- `test_rejected_login[invalid-password]`
- `test_rejected_login[blank-username]`
- `test_rejected_login[blank-password]`
- `test_rejected_login[both-blank]`
- `test_username_length_boundary[below-30]`
- `test_username_length_boundary[at-30]`
- `test_username_length_boundary[above-30]`

### test_login_extended.py

- `test_additional_rejected_credentials[locked-account]`
- `test_additional_rejected_credentials[unknown-account]`
- `test_additional_rejected_credentials[username-case]`
- `test_additional_rejected_credentials[password-case]`
- `test_additional_rejected_credentials[username-spaces]`
- `test_additional_rejected_credentials[password-spaces]`
- `test_other_advertised_accounts_can_authenticate[problem_user]`
- `test_other_advertised_accounts_can_authenticate[performance_glitch_user]`
- `test_other_advertised_accounts_can_authenticate[error_user]`
- `test_other_advertised_accounts_can_authenticate[visual_user]`
- `test_password_input_is_masked`
- `test_login_with_enter_key`
- `test_dismiss_login_error`
- `test_correct_credentials_after_rejection[incorrect-password]`
- `test_correct_credentials_after_rejection[required-fields]`
- `test_protected_pages_in_fresh_session[/inventory.html]`
- `test_protected_pages_in_fresh_session[/cart.html]`
- `test_protected_pages_in_fresh_session[/inventory-item.html?id=4]`
- `test_protected_pages_in_fresh_session[/checkout-step-one.html]`
- `test_protected_pages_in_fresh_session[/checkout-step-two.html]`
- `test_protected_pages_in_fresh_session[/checkout-complete.html]`
- `test_logout_then_login_again`

### test_navigation.py

- `test_menu_opens_and_closes`
- `test_all_items_menu_from_other_screens[cart]`
- `test_all_items_menu_from_other_screens[details]`
- `test_all_items_menu_from_other_screens[information]`
- `test_all_items_menu_from_other_screens[overview]`
- `test_all_items_menu_from_other_screens[complete]`
- `test_reset_app_state_clears_persisted_cart[/inventory.html]`
- `test_reset_app_state_clears_persisted_cart[/cart.html]`
- `test_footer_links_on_each_screen[/inventory.html]`
- `test_footer_links_on_each_screen[/inventory-item.html?id=4]`
- `test_footer_links_on_each_screen[/cart.html]`
- `test_footer_links_on_each_screen[/checkout-step-one.html]`
- `test_footer_links_on_each_screen[/checkout-step-two.html]`
- `test_footer_links_on_each_screen[/checkout-complete.html]`
- `test_logout_from_other_screens[/cart.html]`
- `test_logout_from_other_screens[/inventory-item.html?id=4]`
- `test_logout_from_other_screens[/checkout-step-one.html]`
- `test_logout_from_other_screens[/checkout-step-two.html]`

### test_products.py

- `test_catalog_matches_reviewable_baseline`
- `test_sorting[name-ascending]`
- `test_sorting[name-descending]`
- `test_sorting[price-ascending]`
- `test_sorting[price-descending]`
- `test_sorting_preserves_cart_selection`
- `test_every_product_detail_link[title-sauce-labs-backpack]`
- `test_every_product_detail_link[title-sauce-labs-bike-light]`
- `test_every_product_detail_link[title-sauce-labs-bolt-t-shirt]`
- `test_every_product_detail_link[title-sauce-labs-fleece-jacket]`
- `test_every_product_detail_link[title-sauce-labs-onesie]`
- `test_every_product_detail_link[title-test.allthethings()-t-shirt-(red)]`
- `test_every_product_detail_link[img-sauce-labs-backpack]`
- `test_every_product_detail_link[img-sauce-labs-bike-light]`
- `test_every_product_detail_link[img-sauce-labs-bolt-t-shirt]`
- `test_every_product_detail_link[img-sauce-labs-fleece-jacket]`
- `test_every_product_detail_link[img-sauce-labs-onesie]`
- `test_every_product_detail_link[img-test.allthethings()-t-shirt-(red)]`
- `test_add_and_remove_from_product_details[sauce-labs-backpack]`
- `test_add_and_remove_from_product_details[sauce-labs-bike-light]`
- `test_add_and_remove_from_product_details[sauce-labs-bolt-t-shirt]`
- `test_add_and_remove_from_product_details[sauce-labs-fleece-jacket]`
- `test_add_and_remove_from_product_details[sauce-labs-onesie]`
- `test_add_and_remove_from_product_details[test.allthethings()-t-shirt-(red)]`
- `test_inventory_selection_is_reflected_on_details`
