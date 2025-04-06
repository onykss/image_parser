# остальное
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
# скачивание изображений
import time
# сбор аргументов и проверка браузера
import shutil
import subprocess
import logging

import downloader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler()
    ]
)


def get_urls(query):
    """
    Создает ссылки на запросы в сервисы с использованием ключевых слов

    :param query: Фраза или слово, используемая при поиске
    :return: Ссылки для трех сервисов
    """
    words = query
    google_url = "https://www.google.ru/search?q=" + words.replace("_", "+")
    google_url += "&newwindow=1&sca_esv=3d12d61a3ad17106&biw=1528&bih=834&udm=2"
    google_url += "&ei=1ELfZ6DYJcuJxc8PiLLfkQ8&ved=0ahUKEwigkoOM556MAxXLRPEDHQjZN_IQ4dUDCBE&uact=5&oq="
    google_url += words.replace("_", "+")
    google_url += ("&gs_lp=EgNpbWciC2NhdCBhbmQgZG9nMgoQABiABBhDGIoFMgUQABiABDIFEAAYgAQy"
                   "ChAAGIAEGEMYigUyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAR"
                   "IjyZQ4wRYqiNwAXgAkAEAmAG_AaABjQuqAQMwLji4AQPIAQD4AQGYAgmgAr8LwgINEAAYgAQYsQMYQxi")
    google_url += ("KBcICBhAAGAcYHsICCxAAGIAEGLEDGIMBwgIOEAAYgAQYsQMYgwEYigXCA"
                   "hAQABiABBixAxhDGIMBGIoFmAMAiAYBkgcDMS44oAftJ7IHAzAuOLgHtgs&sclient=img")
    unsplash_url = "https://unsplash.com/s/photos/" + words.replace("_", "-")
    istock_url = "https://www.istockphoto.com/ru/search/2/image?phrase=" + words.replace("_", "%20") + "&page=1"
    return google_url, unsplash_url, istock_url


def parse_images_from_google(url, limit, out_dir, driver, collected_images):
    """
    Собирает ссылки на изображения из Google Images

    :param url: Ссылка на запрос
    :param limit: Предельное количество изображений
    :param out_dir: Директория для загрузки
    :param driver: Webdriver
    :param collected_images: Количество собранных изображений
    :return: Количество собранных изображений за вызов функции.
    """
    logging.info("Поиск изображений в google images...")
    driver.get(url)

    for _ in range(min(((limit - collected_images) // 50) + 1, 20)):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    image_blocks = driver.find_elements(By.TAG_NAME, "img")
    image_urls = []
    for image_block in image_blocks:
        image_url = image_block.get_attribute("src")
        image_height = image_block.get_attribute("height")
        if image_url and int(image_height) > 50:
            if "encrypted" in image_url:
                image_urls.append(image_url)

    imgs_counter = downloader.download_images(limit=limit, image_urls=image_urls, out_dir=out_dir,
                               collected_images=collected_images)

    return imgs_counter


def parse_images_from_unsplash(url, limit, out_dir, driver, collected_images):
    """
    Собирает ссылки на изображения из Unsplash

    :param url: Ссылка на запрос
    :param limit: Предельное количество изображений
    :param out_dir: Директория для загрузки
    :param driver: Webdriver
    :param collected_images: Количество собранных изображений
    :return: Количество собранных изображений за вызов функции.
    """
    logging.info("Поиск изображений в unsplash")

    driver.get(url)
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more')]")
    driver.execute_script("arguments[0].click();", next_button)

    scrolls = min((limit - collected_images) // 20, 10000 // 45)
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

    image_urls = []
    image_blocks = driver.find_elements(By.TAG_NAME, "img")
    for image_block in image_blocks:
        image_url = image_block.get_attribute("src")
        image_height = image_block.get_attribute("height")
        if image_url and int(image_height) > 50:
            image_urls.append(image_url)

    imgs_counter = downloader.download_images(limit=limit, image_urls=image_urls, out_dir=out_dir,
                               collected_images=collected_images)

    return imgs_counter


def get_new_page(driver):
    """
    Загружает новую страницу на сайте IStockPhoto
    И собирает блоки с изображениями

    :param driver: webdriver
    :return: Блоки с изображениями
    """
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "[data-testid=\"pagination-button-next\"]")
        next_url = next_button.get_attribute("href")
        driver.get(next_url)
        image_blocks = driver.find_elements(By.TAG_NAME, "img")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    except NoSuchElementException:
        return None
    return image_blocks


def parse_images_from_istock(url, limit, out_dir, driver, collected_images):
    """
    Собирает ссылки на изображения из IStockPhoto

    :param url: Ссылка на запрос
    :param limit: Предельное количество изображений
    :param out_dir: Директория для загрузки
    :param driver: Webdriver
    :param collected_images: Количество собранных изображений
    :return: Количество собранных изображений за вызов функции.
    """
    logging.info("Поиск изображений в istockphoto")

    driver.get(url)
    image_blocks = driver.find_elements(By.TAG_NAME, "img")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    imgs_counter = 0

    stop = False
    while (collected_images + imgs_counter) <= limit and not stop:
        image_urls = []
        for image_block in image_blocks:
            image_url = image_block.get_attribute("src")
            if "media" in image_url:
                image_urls.append(image_url)

        imgs_counter += downloader.download_images(limit=limit, image_urls=image_urls, out_dir=out_dir,
                                   collected_images=(collected_images + imgs_counter))
        if (collected_images + imgs_counter) < limit:
            image_blocks = get_new_page(driver)
            if not image_blocks:
                break

    return imgs_counter
