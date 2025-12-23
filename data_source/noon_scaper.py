import urllib
import logging
from pathlib import Path

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
from lxml import etree
from pydantic import BaseModel, Field

from config import CACHE_DIR

options = uc.ChromeOptions()
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")


class ProductBriefInfo(BaseModel):
    noon_id: str = Field(description='Id on Noon')
    title: str = Field(description='Title of the product')
    price: float = Field(description='Price of the product')
    rate: float | None = Field(description='Rate of the product')
    rate_amount: int | None = Field(description='Rate amount of the product')
    url: str = Field(description='URL of the product')


def scrape(keyword: str, pages: int = 5, sleep: int = 0):
    """
    Input a keyword and return a list of products
    :param keyword: search keyword
    :param pages: pages to scrape
    :param sleep: sleep time
    :return: list of products
    """
    products = []

    driver = uc.Chrome(options=options)

    try:
        page_no = 0
        while True:
            page_no += 1
            print('Scraping page', page_no)
            # Open the URL
            url = f"https://www.noon.com/saudi-en/search/?q={urllib.parse.quote(keyword)}"
            driver.get(url)

            # Wait for the page to load (you can adjust the sleep time or use WebDriverWait for a more robust solution)
            time.sleep(sleep)

            # Get the page source (HTML content)
            page_source = driver.page_source
            print(page_source[:200])

            # Optionally print the page source or perform other actions
            with open(Path(CACHE_DIR) / f'{keyword}-{int(time.time())}.html', 'w', encoding='utf-8') as f:
                f.write(page_source)

            html = etree.HTML(page_source)
            index = 1

            while True:
                title = html.xpath(
                    f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/h2/text()')
                price = html.xpath(
                    f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div/div[1]/strong/text()')
                if not price:
                    price = html.xpath(
                        f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div[1]/div[1]/strong/text()')
                if not price:
                    price = html.xpath(
                        f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[3]/div[1]/div[1]/strong/text()')
                rate = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div/div[2]/text()')
                rate_amount = html.xpath(
                    f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div/div[3]/span/text()')
                if not rate:
                    rate = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div/div[2]/text()')
                    rate_amount = html.xpath(
                        f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div/div[3]/span/text()')
                if not rate:
                    rate = html.xpath(
                        f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div[1]/text()')
                    rate_amount = html.xpath(
                        f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div[2]/div[2]/span/text()')
                url = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/@href')
                if title:
                    try:
                        product = ProductBriefInfo(
                            noon_id=url[0].split('/')[3],
                            title=title[0],
                            price=price[0],
                            rate=rate[0] if rate else None,
                            rate_amount=rate_amount[0] if rate_amount else None,
                            url=url[0],
                        )
                        products.append(product)
                    except IndexError as e:
                        logging.error(f'Error occurred while scraping the {index}th product: {e}')
                    index += 1
                else:
                    break

            if page_no >= pages:
                break

            next_page_btn = driver.find_element(
                By.XPATH, '//*[@id="catalog-page-container"]/div/div/div[2]/div[5]/div/ul/li[last()]/a'
            )
            next_page_btn.click()
    finally:
        try:
            # Close the browser
            driver.quit()
        except OSError as e:
            pass

    return products

if __name__ == '__main__':
    products = scrape('cat', 1, 3)
    print(len(products))
    for product in products:
        print(product.rate)
