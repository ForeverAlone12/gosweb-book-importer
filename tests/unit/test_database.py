import pytest
import json
from database import Database
from models import Book


class TestDatabase:
    def test_init_db(self, app):
        """Тест инициализации базы данных"""
        with app.app_context():
            db = Database(':memory:')  # Используем in-memory базу
            db.init_db()

            # Проверяем, что таблица создана
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
            result = cursor.fetchone()
            conn.close()

            assert result is not None

    def test_insert_and_retrieve_book(self, app):
        """Тест вставки и получения книги"""
        with app.app_context():
            db = Database(':memory:')
            db.init_db()

            book = Book(
                url='https://test.com',
                name='Test Book',
                authors='Test Author'
            )

            # Вставляем книгу
            book_id = db.insert_book(book)
            assert book_id is not None

            # Получаем книгу
            retrieved = db.get_book_by_id(book_id)
            assert retrieved is not None
            assert retrieved.name == 'Test Book'
            assert retrieved.authors == 'Test Author'

    def test_search_books(self, app):
        """Тест поиска книг"""
        with app.app_context():
            db = Database(':memory:')
            db.init_db()

            # Создаем тестовые книги
            book1 = Book(url='https://test1.com', name='Math Book', authors='Math Author')
            book2 = Book(url='https://test2.com', name='Physics Book', authors='Physics Author')

            db.insert_book(book1)
            db.insert_book(book2)

            # Ищем по названию
            results = db.search_books('Math')
            assert len(results) == 1
            assert results[0].name == 'Math Book'

            # Ищем по автору
            results = db.search_books('Physics')
            assert len(results) == 1
            assert results[0].authors == 'Physics Author'