import urllib.request
import time


def download_images(limit, image_urls, out_dir, collected_images):
    """
    Загружает изображения по ссылкам из image_urls

    :param limit: Предельное количество изображений
    :param image_urls: Ссылки на изображения
    :param out_dir: Директория, в которую происходит загрузка
    :param collected_images: Количество собранных ранее изображений

    :return: Количество изображений, загруженных при вызове функции
    """
    if not image_urls:
        return 0
    length = len(image_urls)
    stop = False
    counter = 0
    while (collected_images + counter) <= limit and not stop:
        filename = f"{out_dir}/{(collected_images + counter)}_{int(time.time() % 100000)}.jpg"
        urllib.request.urlretrieve(image_urls[counter], filename)
        counter += 1
        if counter == length or (collected_images + counter) == limit:
            stop = True

    return counter
