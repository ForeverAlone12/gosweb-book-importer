import pytest
import json
from unittest.mock import patch


class TestAppEndpoints:
    def test_index_page(self, client, db_session):
        """Тест главной страницы"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Web Scraper' in response.data

    def test_scrape_endpoint(self, client, db_session):
        """Тест endpoint'а скрапинга"""
        response = client.post('/scrape', data={
            'url': 'https://example.com'
        }, follow_redirects=True)

        assert response.status_code == 200

    @patch('app.BookService.delete_book')
    def test_delete_endpoint(self, mock_delete, client):
        """Тест endpoint'а удаления"""
        mock_delete.return_value = True

        response = client.post('/delete', data={
            'book_id': '1'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_export_endpoints(self, client, db_session):
        """Тест endpoint'ов экспорта"""
        response = client.get('/export-books')
        assert response.status_code in [200, 404]  # 200 если есть книги, 404 если нет

        response = client.get('/export-csv')
        assert response.status_code in [200, 404]