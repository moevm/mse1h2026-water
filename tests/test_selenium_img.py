from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def test_streamlit_backend_error_zero_zero():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get("http://localhost:8501")

        wait = WebDriverWait(driver, 120)

        lat_input = wait.until(
            lambda d: d.find_element(By.XPATH, "//input[@placeholder='например: 60.123456']")
        )
        lon_input = wait.until(
            lambda d: d.find_element(By.XPATH, "//input[@placeholder='например: 30.123456']")
        )

        lat_input.clear()
        lat_input.send_keys("0")

        lon_input.clear()
        lon_input.send_keys("0")

        btn = wait.until(
            lambda d: d.find_element(By.XPATH, "//button[contains(., 'Проанализировать')]")
        )
        btn.click()
        wait.until(
            lambda d: "Данные с сервера не получены" in d.page_source
        )
        wait.until(
            lambda d: "Ошибка сервера: 500 Server Error" in d.page_source
        )
        page = driver.page_source
        assert "Данные с сервера не получены" in page
        assert "Ошибка сервера: 500 Server Error" in page

    finally:
        driver.quit()