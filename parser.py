
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import shutil
import subprocess
import logging

import downloader

from dotenv import load_dotenv
import os
import requests

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
    freepik = words.replace("_", " ")
    unsplash_url = "https://unsplash.com/s/photos/" + words.replace("_", "-")
    return google_url, unsplash_url, freepik


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


def parse_images_from_freepik(query, limit, out_dir, driver, collected_images):
    """
    Собирает ссылки на изображения из IStockPhoto

    :param query: запрос
    :param limit: Предельное количество изображений
    :param out_dir: Директория для загрузки
    :param driver: Webdriver
    :param collected_images: Количество собранных изображений
    :return: Количество собранных изображений за вызов функции.
    """
    logging.info("Поиск изображений в freepik (необходим API ключ)")

    try:
        load_dotenv()

        api_key = os.getenv("FREEPIK_API_KEY")
        if not api_key:
            logging.error("Не удается получить API ключ")
            return 0
    except:
        logging.info("Для работы с freepik необходим API ключ")
        return 0

    headers = {
        "x-freepik-api-key": api_key
    }

    url = "https://api.freepik.com/v1/resources"

    params = {
        "term": query,
        "page": 1,
        "limit": 100,
        "order": "relevance",
        "filters[license][freemium]": 1,
        "filters[content_type][photo]": 1
    }

    downloaded_count = 0

    while downloaded_count < limit and params["page"] < 100:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            logging.error(f"Ошибка при запросе к API: {response.status_code}, {response.text}")
            break

        data = response.json()
        image_urls = [
            item["image"]["source"]["url"]
            for item in data["data"]
            if "image" in item and "source" in item["image"] and "url" in item["image"]["source"]
        ]

        downloaded_count += downloader.download_images(limit=limit, image_urls=image_urls, out_dir=out_dir,
                                   collected_images=(collected_images + downloaded_count))

        params["page"] += 1

    return downloaded_count

