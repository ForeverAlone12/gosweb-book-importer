import sqlite3
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Book

class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name or os.getenv("SQLITE_DB", "books.db")
        self.init_db()

    def get_connection(self):
        """Получение соединения с базой данных"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Инициализация базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            authors TEXT NOT NULL,
            series TEXT,
            class_from INTEGER NOT NULL,
            class_to INTEGER,
            subject TEXT NOT NULL,
            program TEXT,
            publisher TEXT,
            description TEXT NOT NULL,
            part INTEGER,
            type TEXT,
            type_resourse TEXT,
            is_ovz BOOLEAN NOT NULL DEFAULT FALSE,
            type_pay_resourse TEXT,
            publication_language TEXT,
            image_name TEXT, 
            image_data BLOB,
            image_url TEXT,
            image_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_series ON books (series)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_class_from ON books (class_from)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_class_from_class_to ON books (class_from, class_to)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_subject ON books (subject)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_program ON books (program)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_publisher ON books (publisher)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_part ON books (part)')

        conn.commit()
        conn.close()

    def insert_book(self, book: Book) -> int:
        """Добавление книги в базу данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        #characteristics_json = json.dumps(book.characteristics) if book.characteristics else '{}'
        characteristics_json = {}

        print(f"Вставка данных в БД: {book}")

        try:
            cursor.execute('''
            INSERT INTO books (url, name, authors, series, class_from, class_to, subject, program,
                           publisher, description, part, type, type_resourse, is_ovz, type_pay_resourse,
                           publication_language, image_name, image_data, image_url, image_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (book.url, book.name, book.authors, book.series, book.class_from, book.class_to, book.subject,
            book.program, book.publisher, book.description, book.part, book.type, book.type_resourse,
            book.is_ovz, book.type_pay_resourse, book.publication_language,
            book.image_name, book.image_data, book.image_url, book.image_type,))

            conn.commit()
            inserted_id = cursor.lastrowid

            print(f"Вставка прошла успешнА! {inserted_id}")

            return inserted_id

        except sqlite3.IntegrityError as e:
            print(f"Ошибка вставки: {e}")
            # URL уже существует, возвращаем ID существующей книги
            existing_book = self.get_book_by_url(book.url)
            print(f"Учебник существует: {existing_book}")
            return existing_book.id if existing_book else None
        finally:
            conn.close()


    def update_book_image(self, book_id: int, image_data: bytes, image_url: str, image_type: str) -> bool:
        """Обновление изображения книги"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE books SET image_data = ?, image_url = ?, image_type = ? WHERE id = ?
        ''', (image_data, image_url, image_type, book_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return affected_rows > 0



    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Получение книги по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return self._row_to_book(result)
        return None

    def get_book_by_url(self, url: str) -> Optional[Book]:
        """Получение книги по URL"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books WHERE url = ?', (url,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return self._row_to_book(result)
        return None


    def get_all_books(self, order_by: str = "id", order_direction: str = "DESC") -> List[Book]:
        """Получение всех книг (без данных изображений для производительности)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        valid_columns = ["id", "url", "created_at"]
        order_by = order_by if order_by in valid_columns else "id"
        order_direction = "DESC" if order_direction.upper() == "DESC" else "ASC"

        cursor.execute(f'SELECT * FROM books ORDER BY {order_by} {order_direction}')
        results = cursor.fetchall()
        conn.close()

        return [self._row_to_book(row) for row in results]

    def delete_book(self, book_id: int) -> bool:
        """Удаление книги по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
        affected_rows = cursor.rowcount

        conn.commit()
        conn.close()

        return affected_rows > 0

    def delete_book_by_url(self, url: str) -> bool:
        """Удаление книги по URL"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM books WHERE url = ?', (url,))
        affected_rows = cursor.rowcount

        conn.commit()
        conn.close()

        return affected_rows > 0

    def search_books(self, query: str, search_in_characteristics: bool = True) -> List[Book]:
        """Поиск книг по URL и характеристикам"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books WHERE url LIKE ?', (f'%{query}%',))

        results = cursor.fetchall()
        conn.close()

        return [self._row_to_book_lightweight(row) for row in results]

    def book_exists(self, url: str) -> bool:
        """Проверка существования книги по URL"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM books WHERE url = ?', (url,))
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def update_book_characteristics(self, book_id: int, characteristics: Dict[str, Any]) -> bool:
        """Обновление характеристик книги"""
        conn = self.get_connection()
        cursor = conn.cursor()

        characteristics_json = json.dumps(characteristics)

        cursor.execute('''
        UPDATE books SET characteristics_json = ? WHERE id = ?
        ''', (characteristics_json, book_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return affected_rows > 0

    def update_book_by_url(self, url: str, characteristics: Dict[str, Any]) -> bool:
        """Обновление характеристик книги по URL"""
        conn = self.get_connection()
        cursor = conn.cursor()

        characteristics_json = json.dumps(characteristics)

        cursor.execute('''
        UPDATE books SET characteristics_json = ? WHERE url = ?
        ''', (characteristics_json, url))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return affected_rows > 0

    def _row_to_book(self, row) -> Book:
        """Конвертирует строку из БД в объект Book (с данными изображения)"""
        # characteristics = {}
        # if row['characteristics_json']:
        #     try:
        #         characteristics = json.loads(row['characteristics_json'])
        #     except json.JSONDecodeError:
        #         characteristics = {}

        return Book(
            id=row['id'],
            url=row['url'],
            name=row['name'],
            authors=row['authors'],
            series=row['series'],
            class_from=row['class_from'],
            class_to=row['class_to'],
            subject=row['subject'],
            program=row['program'],
            publisher=row['publisher'],
            description=row['description'],
            part=row['part'],
            type=row['type'],
            type_resourse=row['type_resourse'],
            is_ovz=row['is_ovz'],
            type_pay_resourse=row['type_pay_resourse'],
            publication_language=row['publication_language'],
            image_name=row['image_name'],
            # characteristics=characteristics,
            image_data=row['image_data'] or None,
            image_url=row['image_url'] or None,
            image_type=row['image_type'] or None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def _row_to_book_lightweight(self, row) -> Book:
        """Конвертирует строку из БД в объект Book (без данных изображения)"""
        # characteristics = {}
        # if row['characteristics_json']:
        #     try:
        #         characteristics = json.loads(row['characteristics_json'])
        #     except json.JSONDecodeError:
        #         characteristics = {}

        return Book(
            id=row['id'],
            url=row['url'],
            name=row['name'],
            authors=row['authors'],
            series=row['series'],
            class_from=row['class_from'],
            class_to=row['class_to'],
            subject=row['subject'],
            program=row['program'],
            publisher=row['publisher'],
            description=row['description'],
            part=row['part'],
            type=row['type'],
            type_resourse=row['type_resourse'],
            is_ovz=row['is_ovz'],
            type_pay_resourse=row['type_pay_resourse'],
            publication_language=row['publication_language'],
            image_name=row['image_name'],
            image_url=row['image_url'],
            image_type=row['image_type'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

# Глобальный экземпляр базы данных
db = Database()