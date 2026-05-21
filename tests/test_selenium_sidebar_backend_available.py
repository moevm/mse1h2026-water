import os
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


FRONTEND_URL = os.getenv("SELENIUM_FRONTEND_URL", "http://localhost:8501").rstrip("/")
BACKEND_URL = os.getenv("SELENIUM_BACKEND_URL", "http://localhost:8000").rstrip("/")


def test_sidebar_backend_available():
    with urlopen(f"{BACKEND_URL}/", timeout=5) as response:
        assert response.status == 200

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,1000")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(FRONTEND_URL)
        wait = WebDriverWait(driver, 120)

        wait.until(lambda d: "Бэкенд подключен" in d.find_element(By.TAG_NAME, "body").text)

        body = driver.find_element(By.TAG_NAME, "body").text
        assert "Бэкенд подключен" in body
        assert "Бэкенд не отвечает" not in body
    finally:
        driver.quit()
