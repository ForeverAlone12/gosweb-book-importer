from typing import List, Optional, Dict, Any

from sqlalchemy import or_

from models import BookBase, db
import requests

class BookService:
    @staticmethod
    def create_or_update_book(book_data: Dict[str, Any]) -> BookBase:
        """Создание или обновление книги (если URL уже существует)"""

        # Проверяем, существует ли книга с таким URL
        existing_book = BookBase.query.filter_by(url=book_data.get('url')).first()

        if existing_book:
            # Обновляем существующую книгу
            BookService._update_book_from_dict(existing_book, book_data)
            db.session.commit()
            return existing_book
        else:
            # Создаем новую книгу
            book = BookBase.from_dict(book_data)
            db.session.add(book)
            db.session.commit()
            return book

    @staticmethod
    def _update_book_from_dict(book: BookBase, data: Dict[str, Any]) -> None:
        """Обновление книги из словаря данных"""
        for key, value in data.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)

    @staticmethod
    def download_and_save_image(image_url: str, book_id: int) -> bool:
        """Скачивание и сохранение изображения для книги"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            image_data = response.content
            image_type = response.headers.get('content-type', '').split('/')[-1]

            book = BookBase.query.get(book_id)
            if book:
                book.image_data = image_data
                book.image_url = image_url
                book.image_type = image_type
                db.session.commit()
                return True
            return False

        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return False

    @staticmethod
    def get_book_with_image(book_id: int) -> Optional[BookBase]:
        """Получение книги с данными изображения"""
        return BookBase.query.get(book_id)

    @staticmethod
    def get_book_image_data(book_id: int) -> Optional[bytes]:
        """Получение данных изображения книги"""
        book = BookBase.query.get(book_id)
        return book.image_data if book else None

    @staticmethod
    def update_book_image(book_id: int, image_data: bytes, image_url: str = None, image_type: str = None) -> bool:
        """Обновление изображения книги"""
        book = BookBase.query.get(book_id)
        if book:
            book.image_data = image_data
            book.image_url = image_url
            book.image_type = image_type
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_book(book_id: int) -> Optional[BookBase]:
        """Получение книги по ID"""
        return BookBase.query.get(book_id)

    @staticmethod
    def get_book_by_url(url: str) -> Optional[BookBase]:
        """Получение книги по URL"""
        return BookBase.query.filter_by(url=url).first()

    @staticmethod
    def get_all_books() -> List[BookBase]:
        """Получение всех книг"""
        return BookBase.query.all()

    @staticmethod
    def delete_book(book_id: int) -> bool:
        """Удаление книги по ID"""
        book = BookBase.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_book_by_url(url: str) -> bool:
        """Удаление книги по URL"""
        book = BookBase.query.filter_by(url=url).first()
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False

    @staticmethod
    def search_books(query: str, search_in_characteristics: bool = True) -> List[BookBase]:
        """Поиск книг"""
        if not query:
            return []

        search_pattern = f"%{query}%"

        # Базовый поиск по основным полям
        base_query = BookBase.query.filter(
            or_(
                BookBase.name.ilike(search_pattern),
                BookBase.authors.ilike(search_pattern),
                BookBase.subject.ilike(search_pattern),
                BookBase.publisher.ilike(search_pattern),
                BookBase.description.ilike(search_pattern)
            )
        )

        # Если нужно искать в характеристиках, но у нас теперь нет отдельной таблицы characteristics
        # Характеристики теперь хранятся в основных полях модели
        return base_query.all()

    @staticmethod
    def update_book_characteristics(book_id: int, characteristics: Dict[str, Any]) -> bool:
        """Обновление характеристик книги"""
        book = BookBase.query.get(book_id)
        if book:
            # Маппинг характеристик на поля модели
            field_mapping = {
                'Название': 'name',
                'Линия УМК, серия': 'series',
                'Описание': 'description',
                'Предмет': 'subject',
                'Издательство': 'publisher',
                'Вид литературы': 'type',
                'Язык': 'publication_language',
                'Класс, возраст': None,  # Обрабатывается отдельно
                'Уровень образования': 'program',
                'Часть': 'part',
                'Авторы': 'authors'
            }

            for key, value in characteristics.items():
                field_name = field_mapping.get(key)
                if field_name and hasattr(book, field_name):
                    setattr(book, field_name, value)

            # Обработка класса (если есть в характеристиках)
            if 'Класс, возраст' in characteristics:
                class_info = characteristics['Класс, возраст']
                numbers = re.findall(r"\d+", class_info)
                if numbers:
                    book.class_from = min(map(int, numbers))
                    book.class_to = max(map(int, numbers))

            db.session.commit()
            return True
        return False

    @staticmethod
    def book_exists(url: str) -> bool:
        """Проверка существования книги по URL"""
        return BookBase.query.filter_by(url=url).first() is not None

    @staticmethod
    def get_books_by_characteristic(key: str, value: Any) -> List[BookBase]:
        """Получение книг по конкретной характеристике"""
        field_mapping = {
            'Название': 'name',
            'Линия УМК, серия': 'series',
            'Предмет': 'subject',
            'Издательство': 'publisher',
            'Вид литературы': 'type',
            'Язык': 'publication_language',
            'Уровень образования': 'program',
            'Часть': 'part',
            'Авторы': 'authors'
        }

        field_name = field_mapping.get(key)
        if field_name:
            return BookBase.query.filter(getattr(BookBase, field_name) == value).all()

        # Специальная обработка для классов
        if key == 'Класс, возраст':
            try:
                class_num = int(value)
                return BookBase.query.filter(
                    BookBase.class_from <= class_num,
                    BookBase.class_to >= class_num
                ).all()
            except (ValueError, TypeError):
                return []

        return []

    @staticmethod
    def get_unique_characteristic_values(key: str) -> List[Any]:
        """Получение уникальных значений для конкретной характеристики"""
        field_mapping = {
            'Название': 'name',
            'Линия УМК, серия': 'series',
            'Предмет': 'subject',
            'Издательство': 'publisher',
            'Вид литературы': 'type',
            'Язык': 'publication_language',
            'Уровень образования': 'program',
            'Часть': 'part',
            'Авторы': 'authors'
        }

        field_name = field_mapping.get(key)
        if field_name:
            # Используем distinct для получения уникальных значений
            values = db.session.query(
                getattr(BookBase, field_name)
            ).filter(
                getattr(BookBase, field_name).isnot(None)
            ).distinct().all()

            return [value[0] for value in values if value[0]]

        # Для классов возвращаем диапазон
        if key == 'Класс, возраст':
            min_class = db.session.query(db.func.min(BookBase.class_from)).scalar()
            max_class = db.session.query(db.func.max(BookBase.class_to)).scalar()
            if min_class is not None and max_class is not None:
                return list(range(min_class, max_class + 1))

        return []

    @staticmethod
    def get_books_by_filters(filters: Dict[str, Any]) -> List[BookBase]:
        """Получение книг с фильтрацией по нескольким параметрам"""
        query = BookBase.query

        for field, value in filters.items():
            if value is not None and hasattr(BookBase, field):
                query = query.filter(getattr(BookBase, field) == value)

        return query.all()

    @staticmethod
    def get_books_paginated(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Получение книг с пагинацией"""
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