import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_pin(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get(url)

    driver.maximize_window()
    time.sleep(5)

    driver.find_element(By.ID, "username_or_email").send_keys(os.environ["TWITTER_USERNAME"])
    driver.find_element(By.ID, "password").send_keys(os.environ["TWITTER_PASSWORD"])

    button = driver.find_element(By.ID, "allow")
    button.click()

    time.sleep(5)

    pin = driver.find_element(By.TAG_NAME, "code").get_attribute("innerHTML")
    return pin
