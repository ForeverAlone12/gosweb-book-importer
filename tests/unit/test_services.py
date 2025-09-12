import pytest
from unittest.mock import Mock, patch
from services import BookService, ExportService


class TestBookService:
    def test_create_or_update_book_new(self, db_session, sample_book_data):
        """Тест создания новой книги"""
        book = BookService.create_or_update_book(sample_book_data)

        assert book.id is not None
        assert book.name == 'Test Book'
        assert book.authors == 'Author One, Author Two'
        assert book.url == 'https://example.com/book/1'

    def test_create_or_update_book_existing(self, db_session, sample_book_data):
        """Тест обновления существующей книги"""
        # Создаем первую книгу
        book1 = BookService.create_or_update_book(sample_book_data)

        # Обновляем данные
        updated_data = sample_book_data.copy()
        updated_data['name'] = 'Updated Book Name'

        # Пытаемся создать/обновить с тем же URL
        book2 = BookService.create_or_update_book(updated_data)

        # Должна вернуться та же книга с обновленными данными
        assert book2.id == book1.id
        assert book2.name == 'Updated Book Name'

    @patch('services.requests.get')
    def test_download_and_save_image_success(self, mock_get, db_session):
        """Тест успешного скачивания изображения"""
        # Мок HTTP ответа
        mock_response = Mock()
        mock_response.content = b'test_image_data'
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Создаем тестовую книгу
        book_data = {'url': 'https://example.com', 'name': 'Test Book'}
        book = BookService.create_or_update_book(book_data)

        # Пытаемся скачать изображение
        result = BookService.download_and_save_image('https://example.com/image.jpg', book.id)

        assert result is True

        # Проверяем, что книга обновлена
        updated_book = BookService.get_book(book.id)
        assert updated_book.image_url == 'https://example.com/image.jpg'


class TestExportService:
    def test_export_books_to_csv(self, db_session, sample_book_data):
        """Тест экспорта в CSV"""
        # Создаем тестовые книги
        book1 = BookService.create_or_update_book(sample_book_data)

        book2_data = sample_book_data.copy()
        book2_data['url'] = 'https://example.com/book/2'
        book2_data['name'] = 'Second Book'
        BookService.create_or_update_book(book2_data)

        # Экспортируем
        csv_buffer = ExportService.export_books_to_csv([book1, book2])

        assert csv_buffer is not None
        csv_content = csv_buffer.getvalue().decode('utf-8-sig')

        # Проверяем наличие данных
        assert 'Test Book' in csv_content
        assert 'Second Book' in csv_content
        assert 'Author One' in csv_content