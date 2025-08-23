from typing import List, Optional, Dict, Any
from models import Book
from db import db
import requests

class BookService:
    @staticmethod
    def create_or_update_book(book_data: Dict[str, Any]) -> Book:
        """Создание или обновление книги (если URL уже существует)"""
        
        book = Book.from_dict(book_data)

        # Проверяем, существует ли книга с таким URL
        existing_book = db.get_book_by_url(book.url)

        if existing_book:
            # Обновляем характеристики существующей книги
            if book.characteristics:
                db.update_book_by_url(book.url, book.characteristics)
            return db.get_book_by_url(book.url)
        else:
            # Создаем новую книгу
            book_id = db.insert_book(book)
            return db.get_book_by_id(book_id)

    @staticmethod
    def download_and_save_image(image_url: str, book_id: int) -> bool:
        """Скачивание и сохранение изображения для книги"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            image_data = response.content
            image_type = response.headers.get('content-type', '').split('/')[-1]

            return db.update_book_image(book_id, image_data, image_url, image_type)

        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return False

    @staticmethod
    def get_book_with_image(book_id: int) -> Optional[Book]:
        """Получение книги с данными изображения"""
        return db.get_book_by_id(book_id)

    @staticmethod
    def get_book_image_data(book_id: int) -> Optional[bytes]:
        """Получение данных изображения книги"""
        book = db.get_book_by_id(book_id)
        return book.image_data if book else None

    @staticmethod
    def update_book_image(book_id: int, image_data: bytes, image_url: str = None, image_type: str = None) -> bool:
        """Обновление изображения книги"""
        return db.update_book_image(book_id, image_data, image_url, image_type)

    @staticmethod
    def get_book(book_id: int) -> Optional[Book]:
        """Получение книги по ID"""
        return db.get_book_by_id(book_id)

    @staticmethod
    def get_book_by_url(url: str) -> Optional[Book]:
        """Получение книги по URL"""
        return db.get_book_by_url(url)

    @staticmethod
    def get_all_books() -> List[Book]:
        """Получение всех книг"""
        return db.get_all_books()


    @staticmethod
    def delete_book(book_id: int) -> bool:
        """Удаление книги по ID"""
        return db.delete_book(book_id)

    @staticmethod
    def delete_book_by_url(url: str) -> bool:
        """Удаление книги по URL"""
        return db.delete_book_by_url(url)

    @staticmethod
    def search_books(query: str, search_in_characteristics: bool = True) -> List[Book]:
        """Поиск книг"""
        return db.search_books(query, search_in_characteristics)

    @staticmethod
    def update_book_characteristics(book_id: int, characteristics: Dict[str, Any]) -> bool:
        """Обновление характеристик книги"""
        return db.update_book_characteristics(book_id, characteristics)

    @staticmethod
    def book_exists(url: str) -> bool:
        """Проверка существования книги по URL"""
        return db.book_exists(url)

    @staticmethod
    def get_books_by_characteristic(key: str, value: Any) -> List[Book]:
        """Получение книг по конкретной характеристике"""
        all_books = db.get_all_books()
        return [
            book for book in all_books
            if book.characteristics and book.characteristics.get(key) == value
        ]


    @staticmethod
    def get_unique_characteristic_values(key: str) -> List[Any]:
        """Получение уникальных значений для конкретной характеристики"""
        all_books = db.get_all_books()
        values = set()
        for book in all_books:
            if book.characteristics and key in book.characteristics:
                values.add(book.characteristics[key])
        return list(values)