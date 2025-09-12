"""Сервисы для работы с книгами."""

from typing import List, Optional, Dict, Any
import requests
import re
import base64
from datetime import datetime

from sqlalchemy import or_
from transliterate import translit

from models import BookBase, BookCharacteristick, db


class BookService:
    """Сервис для работы с книгами."""

    @staticmethod
    def extract_classes(class_str: str) -> tuple[Optional[int], Optional[int]]:
        """Извлечение классов из строки."""
        if not class_str:
            return None, None

        numbers = re.findall(r"\d+", class_str)
        if numbers:
            numbers_int = list(map(int, numbers))
            return min(numbers_int), max(numbers_int)
        return None, None

    @staticmethod
    def generate_image_name(subject: str, class_from: int, part: int) -> str:
        """Генерация имени файла изображения."""
        if not subject:
            return "image"

        # Транслитерация и очистка
        subject_clean = re.sub(r'[ьъ]', '', subject)
        image_name = translit(subject_clean, reversed=True)
        image_name = re.sub(r'\s+', '_', image_name)
        image_name = re.sub(r'[^\w_]', '', image_name)  # Удаляем спецсимволы

        return f"{image_name}_{class_from}_{part}" if class_from and part else image_name

    @staticmethod
    def process_raw_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сырых данных и преобразование в структурированные."""
        processed_data = {}

        # Обрабатываем классы
        class_str = raw_data.get(BookCharacteristick.CLASSES, '')
        class_from, class_to = BookService.extract_classes(class_str)

        # Генерируем имя изображения
        subject = raw_data.get(BookCharacteristick.SUBJECT, '')
        part = raw_data.get(BookCharacteristick.PART, '')
        image_name = BookService.generate_image_name(subject, class_from, part)

        # Обрабатываем изображение
        image_data = None
        if raw_data.get('image_data_base64'):
            try:
                image_data = base64.b64decode(raw_data['image_data_base64'])
            except (ValueError, TypeError):
                image_data = None

        # Формируем структурированные данные
        processed_data = {
            'url': raw_data.get('url'),
            'name': raw_data.get(BookCharacteristick.NAME),
            'authors': raw_data.get(BookCharacteristick.AUTHORS),
            'series': raw_data.get(BookCharacteristick.SERIES),
            'class_from': class_from,
            'class_to': class_to,
            'subject': raw_data.get(BookCharacteristick.SUBJECT),
            'program': raw_data.get(BookCharacteristick.PROGRAM),
            'publisher': raw_data.get(BookCharacteristick.PUBLISHER),
            'description': raw_data.get(BookCharacteristick.DESCRIPTION),
            'part': raw_data.get(BookCharacteristick.PART),
            'type': raw_data.get(BookCharacteristick.TYPE),
            'type_resourse': raw_data.get('type_resourse', ''),
            'is_ovz': raw_data.get('is_ovz', False),
            'type_pay_resourse': raw_data.get('type_pay_resourse', ''),
            'publication_language': raw_data.get(BookCharacteristick.PUBLICATION_LANGUAGE, ''),
            'image_name': image_name,
            'image_data': image_data,
            'image_url': raw_data.get('image_src'),
            'image_type': raw_data.get('image_type'),
            'created_at': datetime.fromisoformat(raw_data['created_at']) if raw_data.get('created_at') else None
        }

        # Очищаем None значения
        return {k: v for k, v in processed_data.items() if v is not None}
    
    @staticmethod
    def create_or_update_book(raw_data: Dict[str, Any]) -> BookBase:
        """Создание или обновление книги из сырых данных."""
        # Обрабатываем сырые данные
        processed_data = BookService.process_raw_data(raw_data)
        
        # Проверяем, существует ли книга с таким URL
        existing_book = BookBase.query.filter_by(url=processed_data.get('url')).first()

        if existing_book:
            # Обновляем существующую книгу
            BookService._update_book_from_dict(existing_book, processed_data)
            db.session.commit()
            return existing_book
        else:
            # Создаем новую книгу
            book = BookBase(**processed_data)
            db.session.add(book)
            db.session.commit()
            return book
    
    @staticmethod
    def _update_book_from_dict(book: BookBase, update_data: Dict[str, Any]) -> None:
        """Обновление книги из словаря данных."""
        for key, value in update_data.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)
    
    @staticmethod
    def download_and_save_image(image_url: str, book_id: int) -> bool:
        """Скачивание и сохранение изображения для книги."""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            image_data = response.content
            image_type = response.headers.get('content-type', '').split('/')[-1]

            book = BookBase.query.get(book_id)
            if book:
                book.set_image(image_data, image_url, image_type)
                db.session.commit()
                return True
            return False

        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return False
    
    @staticmethod
    def get_book_with_image(book_id: int) -> Optional[BookBase]:
        """Получение книги с данными изображения."""
        return BookBase.query.get(book_id)
    
    @staticmethod
    def get_book_image_data(book_id: int) -> Optional[bytes]:
        """Получение данных изображения книги."""
        book = BookBase.query.get(book_id)
        return book.image_data if book else None
    
    @staticmethod
    def update_book_image(book_id: int, image_data: bytes, image_url: str = None, image_type: str = None) -> bool:
        """Обновление изображения книги."""
        book = BookBase.query.get(book_id)
        if book:
            book.set_image(image_data, image_url, image_type)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_book(book_id: int) -> Optional[BookBase]:
        """Получение книги по ID."""
        return BookBase.query.get(book_id)
    
    @staticmethod
    def get_book_by_url(url: str) -> Optional[BookBase]:
        """Получение книги по URL."""
        return BookBase.query.filter_by(url=url).first()
    
    @staticmethod
    def get_all_books() -> List[BookBase]:
        """Получение всех книг."""
        return BookBase.query.all()
    
    @staticmethod
    def delete_book(book_id: int) -> bool:
        """Удаление книги по ID."""
        book = BookBase.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_book_by_url(url: str) -> bool:
        """Удаление книги по URL."""
        book = BookBase.query.filter_by(url=url).first()
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def search_books(query: str) -> List[BookBase]:
        """Поиск книг."""
        if not query:
            return []
        
        search_pattern = f"%{query}%"
        return BookBase.query.filter(
            or_(
                BookBase.name.ilike(search_pattern),
                BookBase.authors.ilike(search_pattern),
                BookBase.subject.ilike(search_pattern),
                BookBase.publisher.ilike(search_pattern),
                BookBase.description.ilike(search_pattern)
            )
        ).all()
    
    @staticmethod
    def book_exists(url: str) -> bool:
        """Проверка существования книги по URL."""
        return BookBase.query.filter_by(url=url).first() is not None
    
    @staticmethod
    def get_books_paginated(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Получение книг с пагинацией."""
        pagination = BookBase.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'books': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_books_by_filters(filters: Dict[str, Any]) -> List[BookBase]:
        """Получение книг с фильтрацией."""
        query = BookBase.query
        
        for field, value in filters.items():
            if value is not None and hasattr(BookBase, field):
                query = query.filter(getattr(BookBase, field) == value)
        
        return query.all()
    
    @staticmethod
    def get_unique_values(field: str) -> List[Any]:
        """Получение уникальных значений поля."""
        if hasattr(BookBase, field):
            values = db.session.query(
                getattr(BookBase, field)
            ).filter(
                getattr(BookBase, field).isnot(None)
            ).distinct().all()
            
            return [value[0] for value in values if value[0] is not None]
        return []