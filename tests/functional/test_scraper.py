import pytest
from unittest.mock import patch, MagicMock
from scraper import Scrapper
from browser_detector import BrowserDetector


class TestScrapper:
    @patch('scraper.webdriver.Chrome')
    def test_scraper_initialization(self, mock_chrome):
        """Тест инициализации скрапера"""
        scraper = Scrapper(browser='chrome', headless=True)

        assert scraper.browser == 'chrome'
        assert scraper.headless is True

    @patch('scraper.webdriver.Chrome')
    @patch('scraper.time.sleep')
    def test_scrape_with_selenium(self, mock_sleep, mock_chrome):
        """Тест метода скрапинга"""
        # Настраиваем мок драйвера
        mock_driver = MagicMock()
        mock_driver.title = 'Test Page'
        mock_driver.page_source = '<html>test</html>'
        mock_chrome.return_value = mock_driver

        scraper = Scrapper(browser='chrome')
        result = scraper.scrape_with_selenium('https://example.com')

        assert result['url'] == 'https://example.com'
        assert result['title'] == 'Test Page'
        assert result['browser_used'] == 'chrome'
        mock_driver.get.assert_called_with('https://example.com')
        mock_driver.quit.assert_called()


class TestBrowserDetector:
    @patch('browser_detector.subprocess.run')
    def test_get_default_browser_windows(self, mock_run):
        """Тест определения браузера в Windows"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'ProgId    REG_SZ    ChromeHTML'
        mock_run.return_value = mock_result

        detector = BrowserDetector()
        # Мокируем platform для Windows
        with patch('browser_detector.platform.system', return_value='Windows'):
            browser = detector.get_default_browser()

        assert browser == 'chrome'