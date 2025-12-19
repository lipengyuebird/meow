import urllib
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
from lxml import etree
from pydantic import BaseModel, Field

from config import CACHE_DIR

# Set up Edge options
edge_options = Options()

# Path to the msedgedriver executable (Edge WebDriver)
driver_path = 'C:\\Users\\lipen\\PycharmProjects\\meow\\msedgedriver.exe'  # Update this with the path to your msedgedriver

# Initialize WebDriver
service = Service(executable_path=driver_path)



class ProductBriefInfo(BaseModel):
    title: str = Field(description='Title of the product')
    price: float = Field(description='Price of the product')
    # rate: float = Field(description='Rate of the product')
    # rate_amount: int = Field(description='Rate amount of the product')
    # url: str = Field(description='URL of the product')


def scrape(keyword: str, sleep: int = 0):
    """
    Input a keyword and return a list of products
    :param keyword: search keyword
    :param sleep: sleep time
    :return: list of products
    """
    driver = webdriver.Edge(service=service, options=edge_options)

    # Open the URL
    url = f"https://www.noon.com/saudi-en/search/?q={urllib.parse.quote(keyword)}"
    driver.get(url)

    # Wait for the page to load (you can adjust the sleep time or use WebDriverWait for a more robust solution)
    time.sleep(sleep)

    # Get the page source (HTML content)
    page_source = driver.page_source

    # Optionally print the page source or perform other actions
    with open(Path(CACHE_DIR) / f'{keyword}-{int(time.time())}.html', 'w', encoding='utf-8') as f:
        f.write(page_source)

    html =  etree.HTML(page_source)
    index = 1
    products = []
    while True:
        title = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/h2/text()')
        price = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[2]/div/div[1]/strong/text()')
        if not price:
            price = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div[1]/div[1]/strong/text()')
        if not price:
            price = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[3]/div[1]/div[1]/strong/text()')
        # rate = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div/div[2]/text()')
        # rate_amount = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/div[1]/div/div[3]/span/text()')
        # url = html.xpath(f'//*[@id="catalog-page-container"]/div/div/div[2]/div[4]/div[{index}]/a/div[1]/div[2]/h2/@href')
        if title:
            try:
                product = ProductBriefInfo(
                    title=title[0],
                    price=price[0],
                )
                products.append(product)
            except IndexError as e:
                logging.error(f'Error occurred while scraping the {index}th product: {e}')
            index += 1
        else:
            break
    # Close the browser
    driver.quit()
    return products

if __name__ == '__main__':
    print(scrape('cat'))
