from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_streamlit_coordinates():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("http://localhost:8501")

    try:
        wait = WebDriverWait(driver, 120)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        lat_locator = (By.XPATH, "//input[@placeholder='например: 60.123456']")
        lon_locator = (By.XPATH, "//input[@placeholder='например: 30.123456']")

        lat_input = wait.until(EC.presence_of_element_located(lat_locator))
        lat_input.clear()
        lat_input.send_keys("59.9386")

        lon_input = wait.until(EC.presence_of_element_located(lon_locator))
        lon_input.clear()
        lon_input.send_keys("30.3141")

        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Проанализировать')]")))
        btn.click()

        wait.until(lambda d: "Экологический статус" in d.find_element(By.TAG_NAME, "body").text)
        wait.until(lambda d: "polluted_percentage" in d.find_element(By.TAG_NAME, "body").text)

        body = driver.find_element(By.TAG_NAME, "body").text
        assert "Экологический статус" in body
        assert "polluted_percentage" in body
        assert "7.35" in body
        
    finally:
        driver.quit()