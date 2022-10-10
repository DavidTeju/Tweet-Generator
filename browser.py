import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver_path = ChromeDriverManager().install()


def get_pin(url):
    options = Options()
    options.headless = True
    # options.binary_location = os.environ["GOOGLE_CHROME_BIN"]
    # TODO: add this to ReadMe
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    driver.get(url)

    time.sleep(5)

    driver.find_element(By.ID, "username_or_email").send_keys(os.environ["TWITTER_USERNAME"])
    driver.find_element(By.ID, "password").send_keys(os.environ["TWITTER_PASSWORD"])

    button = driver.find_element(By.ID, "allow")
    button.click()

    time.sleep(5)

    pin = driver.find_element(By.TAG_NAME, "code").get_attribute("innerHTML")
    return pin
