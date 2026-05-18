import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


FRONTEND_URL = os.getenv(
    "SELENIUM_FRONTEND_URL",
    "http://localhost:8501"
).rstrip("/")


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    yield driver
    driver.quit()


def test_invalid_coordinates(driver):
    driver.get(FRONTEND_URL)
    wait = WebDriverWait(driver, 30)

    lat_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='Широта']")
        )
    )

    lon_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='Долгота']")
        )
    )

    lat_input.clear()
    lat_input.send_keys("999")

    lon_input.clear()
    lon_input.send_keys("30")

    driver.find_element(
        By.XPATH,
        "//button[contains(., 'Проанализировать')]"
    ).click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.TAG_NAME, "body"),
            "Широта должна быть от -90 до 90"
        )
    )

    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Широта должна быть от -90 до 90" in body


def test_invalid_longitude(driver):
    driver.get(FRONTEND_URL)
    wait = WebDriverWait(driver, 30)

    lat_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='Широта']")
        )
    )

    lon_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='Долгота']")
        )
    )

    lat_input.clear()
    lat_input.send_keys("50")

    lon_input.clear()
    lon_input.send_keys("999")

    driver.find_element(
        By.XPATH,
        "//button[contains(., 'Проанализировать')]"
    ).click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.TAG_NAME, "body"),
            "Долгота должна быть от -180 до 180"
        )
    )

    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Долгота должна быть от -180 до 180" in body