# Tests for login_locators
"""Unit tests for the login page locators.
Ensures each selector is a non‑empty string and contains expected Playwright patterns.
"""

from senna.systems.servicos_ti.locators import login_locators as loc


def test_login_locators_non_empty() -> None:
    assert loc.NAV_ENTRAR_LINK
    assert loc.USERNAME_INPUT
    assert loc.PASSWORD_INPUT
    assert loc.SUBMIT_BUTTON


def test_login_locators_patterns() -> None:
    # Simple pattern checks – they must contain Playwright role selector syntax
    selectors = [
        loc.NAV_ENTRAR_LINK,
        loc.USERNAME_INPUT,
        loc.PASSWORD_INPUT,
        loc.SUBMIT_BUTTON,
    ]
    for selector in selectors:
        assert "role=" in selector or "input" in selector
