import pytest
from datetime import datetime
from models import Book


class TestBookModel:
    def test_book_creation(self):
        """Тест создания объекта книги"""
        book = Book(
            name='Test Book',
            authors='Test Author',
            url='https://example.com'
        )

        assert book.name == 'Test Book'
        assert book.authors == 'Test Author'
        assert book.url == 'https://example.com'
        assert book.characteristics is None

    def test_book_to_dict(self):
        """Тест преобразования в словарь"""
        book = Book(
            id=1,
            name='Test Book',
            url='https://example.com'
        )

        result = book.to_dict()

        assert result['id'] == 1
        assert result['name'] == 'Test Book'
        assert result['url'] == 'https://example.com'
        assert 'characteristics' in result

    def test_update_from_characteristics(self):
        """Тест обновления полей из характеристик"""
        book = Book()
        book.characteristics = {
            'Name': 'Book from Characteristics',
            'Authors': 'Characteristic Author',
            'Series': 'Test Series',
            'Program': 'Test Program',
            'Publisher': 'Test Publisher',
            'Description': 'Test description',
            'Class': '10',
            'PublicationLanguage': 'English'
        }

        book.update_from_characteristics()

        assert book.name == 'Book from Characteristics'
        assert book.authors == 'Characteristic Author'
        assert book.series == 'Test Series'
        assert book.program == 'Test Program'
        assert book.publisher == 'Test Publisher'
        assert book.description == 'Test description'
        assert book.class_level == '10'
        assert book.publication_language == 'English'

    def test_get_characteristic(self):
        """Тест получения характеристики"""
        book = Book()
        book.characteristics = {'test_key': 'test_value'}

        assert book.get_characteristic('test_key') == 'test_value'
        assert book.get_characteristic('nonexistent') is None
        assert book.get_characteristic('nonexistent', 'default') == 'default'