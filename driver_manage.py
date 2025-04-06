from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FoxService
from selenium.webdriver.firefox.options import Options as FoxOptions


class DriverManager:
    """
    Класс для управления работы webdriver
    """
    def __init__(self, browser):
        self.driver = self._create_webdriver(browser=browser)

    @staticmethod
    def _create_webdriver(browser):
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--log-level=3")
            return webdriver.Chrome(
                service=ChromeService(),
                options=options
            )
        elif browser == "edge":
            options = EdgeOptions()
            options.add_argument("--headless")
            options.add_argument("--log-level=3")
            options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки сертификатов
            options.add_argument("--disable-web-security")  # Отключить проверку безопасности
            options.add_argument("--allow-running-insecure-content")  # Разрешить небезопасный контент
            options.add_argument("--disable-features=NetworkService")  # Отключить NetworkService
            return webdriver.Edge(
                service=EdgeService(),
                options=options
            )
        elif browser == "firefox":
            options = FoxOptions()
            options.add_argument("--headless")
            return webdriver.Firefox(
                service=FoxService(),
                options=options
            )

    def quit(self):
        if self.driver:
            self.driver.quit()

    def get_driver(self):
        return self.driver
