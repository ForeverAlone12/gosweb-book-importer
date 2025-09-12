import pytest
from unittest.mock import patch, MagicMock
from app import scrape
from services import BookService


class TestScrapingFlow:
    @patch('app.ScrapingThread')
    @patch('app.flash')
    def test_scraping_flow(self, mock_flash, mock_thread, client, db_session):
        """Тест полного потока скрапинга"""
        # Мок потока
        mock_instance = MagicMock()
        mock_thread.return_value = mock_instance

        response = client.post('/scrape', data={
            'url': 'https://example.com/test-book'
        }, follow_redirects=True)

        assert response.status_code == 200
        mock_thread.assert_called_once()
        mock_instance.start.assert_called_once()
        mock_flash.assert_called()