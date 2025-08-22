from dotenv import load_dotenv
from selenium.webdriver import ActionChains
from transliterate import translit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import re
import json
import wget

class Scrapper:

    def __init__(self):
        load_dotenv()

        self.characteristic_names = json.loads(os.getenv('CHARACTERISTIC_NAMES'))
        self.browser_options = json.loads(os.getenv('BROWSER_OPTIONS'))
        self.image_save_path = os.getenv('IMAGE_SAVE_PATH', 'static')
        self.options = self._init_browser_options()


    def _init_browser_options(self):
        options = Options()
        for option in self.browser_options:
            options.add_argument(option)
        return options


    def scrape_with_selenium(self, url):        
    
        driver = webdriver.Chrome(options=self.options)
        actions = ActionChains(driver)
    
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            characteristics ={ 'url': url}
            self._find_title(driver, characteristics)
            self._find_description(driver, characteristics)
            self._find_characteristics(driver, characteristics)
            self._characteristics_post_processing(characteristics)

            img_src = self._find_image_src(driver)

            path = self.image_save_path + "/" + self._create_image_name(img_src, characteristics)
            image = wget.download(img_src, out=path)
            characteristics['src'] = image

            return characteristics
        finally:
            driver.quit()


    def _find_title(self, driver, characteristics):
        title = driver.find_element(By.TAG_NAME, "h1")
        characteristics['Title'] = title.text


    def _find_description(self, driver, characteristics):
        description_block = driver.find_element(By.ID, "description")
        description = description_block.find_element(By.TAG_NAME, "div")
        characteristics['Description'] = description.text


    def _find_characteristics(self, driver, characteristics):
        div_show_characteristics = driver.find_element(By.XPATH, '//div[contains(@class, "DetailBlock_mobile")]')
        if div_show_characteristics.text.__eq__('Развернуть характеристики'):
            btn_show_characteristics = div_show_characteristics.find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", btn_show_characteristics)

        characteristics_items = driver.find_elements(By.XPATH, '//li[contains(@class, "CharacteristicItem")]')
    
        for characteristics_item in characteristics_items:
            name = characteristics_item.find_element(By.TAG_NAME, "span").text
            value = characteristics_item.find_element(By.TAG_NAME, "ul").text
            characteristics[self.characteristic_names.get(name, name)] = value

    def _characteristics_post_processing(self, characteristics):
        self._get_class_period(characteristics)


    def _get_class_period(self, characteristics):
        numbers_class = re.findall(r"\d+", characteristics['class'])
        characteristics['start'] = min(numbers_class)
        characteristics['end'] = max(numbers_class)


    def _find_image_src(self, driver):
        image_blocks = driver.find_element(By.XPATH, '//div[contains(@class, "swiper-wrapper")]')
        img = image_blocks.find_elements(By.TAG_NAME, "img")
        return img[0].get_attribute("src")


    def _create_image_name(self, img_src, characteristics):
        extension = img_src[img_src.rfind("."):]
        part = characteristics.get('part') or ""
        end = characteristics.get('end') or ""
        image_rus_name ="_".join([characteristics['subject'], characteristics['start'], end, part, extension])
        return translit(image_rus_name, reversed=True)
