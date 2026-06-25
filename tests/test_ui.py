import pytest
from playwright.sync_api import expect

BASE_URL = "http://127.0.0.1:8000"


def test_page_loads(page):
    """Home page returns 200 and shows the calculator."""
    page.goto(BASE_URL)
    expect(page.locator("h1")).to_contain_text("Gin")


def test_input_fields_present(page):
    """All three inputs are visible: volume, spirit ABV, target ABV."""
    page.goto(BASE_URL)
    expect(page.locator("#volume")).to_be_visible()
    expect(page.locator("#input_spirit_abv")).to_be_visible()
    expect(page.locator("#target_abv")).to_be_visible()


def test_recipe_dropdown_populated(page):
    """Recipe dropdown contains at least one option with a real value."""
    page.goto(BASE_URL)
    options = page.locator("#recipe_select option")
    count = options.count()
    assert count >= 1
    # Verify at least one option has text content
    first_text = options.first.inner_text()
    assert len(first_text.strip()) > 0


def test_target_abv_prefills_from_recipe(page):
    """After page load, target ABV field is pre-filled from the default recipe (≥ 10)."""
    page.goto(BASE_URL)
    page.wait_for_function("document.getElementById('target_abv').value !== ''")
    value = page.input_value("#target_abv")
    assert float(value) >= 10.0, f"Expected target_abv >= 10, got {value}"


def test_calculate_formula(page):
    """1.5 L / 96% spirit / 40% target → spirit ≈ 0.63 L, water ≈ 0.88 L."""
    page.goto(BASE_URL)
    page.wait_for_function("document.getElementById('target_abv').value !== ''")

    page.fill("#volume", "1.5")
    page.fill("#input_spirit_abv", "96")
    page.fill("#target_abv", "40")

    # Wait for debounced JS calculate to produce the expected result
    page.wait_for_function(
        "() => document.getElementById('spirit-value').textContent === '0.63'",
        timeout=5000,
    )

    spirit = page.inner_text("#spirit-value")
    water  = page.inner_text("#water-value")

    assert "0.63" in spirit, f"Wrong spirit value: {spirit!r}"
    assert "0.87" in water,  f"Wrong water value: {water!r}"