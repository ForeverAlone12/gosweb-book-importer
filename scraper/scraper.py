from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import BookCharacteristick

import os
import json

class Scraper:

    def __init__(self):
        load_dotenv()
        self.browser_options = json.loads(os.getenv('BROWSER_OPTIONS'))
        self.options = self._init_browser_options()


    def _init_browser_options(self):
        options = Options()
        for option in self.browser_options:
            options.add_argument(option)
        return options


    def scrape_with_selenium(self, url):        
        """Извлекает данные учебника по ссылке."""
    
        driver = webdriver.Chrome(options=self.options)
    
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            characteristics = { 'url':url }
            self._parse_name(driver, characteristics)
            self._parse_description(driver, characteristics)
            self._parse_characteristics(driver, characteristics)
            self._parse_image_src(driver, characteristics)

            return characteristics
        finally:
            driver.quit()


    def _parse_name(self, driver, characteristics):
        """Извлекает название учебника."""
        name = driver.find_element(By.TAG_NAME, "h1")
        characteristics[BookCharacteristick.NAME] = name.text


    def _parse_description(self, driver, characteristics):
        """Извлекает описание учебника."""
        description_block = driver.find_element(By.ID, "description")
        description = description_block.find_element(By.TAG_NAME, "div")
        characteristics[BookCharacteristick.DESCRIPTION] = description.text


    def _parse_characteristics(self, driver, characteristics):
        """Извлекает все характеристики учебника."""

        # Иногда часть характеристик скрыта, надо их раскрыть
        div_show_characteristics = driver.find_element(By.XPATH, '//div[contains(@class, "DetailBlock_mobile")]')
        if div_show_characteristics.text.__eq__('Развернуть характеристики'):
            btn_show_characteristics = div_show_characteristics.find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", btn_show_characteristics)

        characteristics_items = driver.find_elements(By.XPATH, '//li[contains(@class, "CharacteristicItem")]')
    
        for characteristics_item in characteristics_items:
            name = characteristics_item.find_element(By.TAG_NAME, "span").text
            value = characteristics_item.find_element(By.TAG_NAME, "ul").text
            characteristics[name] = value

    def _parse_image_src(self, driver, characteristics):
        """Извлекает ссылку на обложку учебника."""
        image_blocks = driver.find_element(By.XPATH, '//div[contains(@class, "swiper-wrapper")]')
        img = image_blocks.find_elements(By.TAG_NAME, "img")
        characteristics[BookCharacteristick.IMAGE_SRC] = img[0].get_attribute("src")