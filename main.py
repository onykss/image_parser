import argparse
import parser
import logging
import os
from driver_manage import DriverManager
from selenium.common.exceptions import WebDriverException


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler()
    ]
)


def main():
    collected_images = 0

    arg_parser = argparse.ArgumentParser(description="Парсер изображений из открытых источников"
                                                 "\n(google images, unsplash, freepic)")
    arg_parser.add_argument("--query", required=True,
                        help="Ключевое слово для поиска изображений. Если используется фраза, "
                             "то записывать слова нужно через \"_\"")
    arg_parser.add_argument("--limit", type=int, required=True, help="Необходимое количество изображений")
    arg_parser.add_argument("--output_dir", default="./images",
                        help="Директория для сохранения изображений, в формате \"./name\"")
    arg_parser.add_argument("--browser", required=True, choices=['chrome', 'edge', 'firefox'],
                        help="Браузер, используемый программой")

    args = arg_parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    google_url, unsplash_url, freepik = parser.get_urls(args.query)
    manager = DriverManager(args.browser)
    driver = manager.get_driver()

    try:
        driver.get("https://www.google.com")
        logging.info("Соединение с браузером установлено")

        collected_images += parser.parse_images_from_freepik(freepik, args.limit, args.output_dir, driver,
                                                            collected_images)
        if collected_images < args.limit:
            collected_images += parser.parse_images_from_google(google_url, args.limit, args.output_dir, driver,
                                                                collected_images)
        if collected_images < args.limit:
            collected_images += parser.parse_images_from_unsplash(unsplash_url, args.limit, args.output_dir, driver,
                                                                  collected_images)
        logging.info(f"{collected_images} изображений собрано")
    except WebDriverException as e:
        logging.error(f"Не удается подключиться к браузеру: {e}!")

    manager.quit()


if __name__ == "__main__":
    main()
