import os

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


FRONTEND_URL = os.getenv("SELENIUM_FRONTEND_URL", "http://localhost:8501").rstrip("/")
BACKEND_URL = os.getenv(
    "SELENIUM_BACKEND_URL",
    os.getenv("BACKEND_URL", "http://localhost:8000"),
).rstrip("/")


def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


RUN_BACKEND_UNAVAILABLE_TEST = not check_backend_health()


@pytest.mark.skipif(
    not RUN_BACKEND_UNAVAILABLE_TEST,
    reason="requires frontend running with backend unavailable",
)
def test_sidebar_backend_unavailable():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(FRONTEND_URL)
        wait = WebDriverWait(driver, 120)

        wait.until(lambda d: "Бэкенд не отвечает" in d.find_element(By.TAG_NAME, "body").text)

        body = driver.find_element(By.TAG_NAME, "body").text
        assert "Бэкенд не отвечает" in body
        assert "Бэкенд подключен" not in body
    finally:
        driver.quit()
