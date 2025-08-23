import csv
import io
import re
from  zipfile import ZipFile, ZIP_DEFLATED
from typing import List
from models import Book, BookCharacteristick
from services import BookService
from transliterate import translit

class ExportService:
    @staticmethod
    def export_books_to_zip(books: List[Book]) -> io.BytesIO:
        """Экспорт всех книг в ZIP архив"""
        zip_buffer = io.BytesIO()

        with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zip_file:
            # Добавляем CSV файл
            csv_data = ExportService._create_csv_data(books)
            # ToDo: название файла csv вынести в настройки
            zip_file.writestr('books_import.csv', csv_data)

            # Добавляем изображения
            ExportService._add_images_to_zip(zip_file, books)

        zip_buffer.seek(0)
        return zip_buffer

    @staticmethod
    def _create_csv_data(books: List[Book]) -> bytes:
        """Создание CSV данных для всех книг"""

        csv_buffer = io.BytesIO()
        # csv_buffer.write(b'\xEF\xBB\xBF')  # BOM для UTF-8

        csv_writer = csv.writer(
            io.TextIOWrapper(csv_buffer, encoding='utf-8-sig', newline='', write_through=True)
        )

        headers = ['Image', 'Name', 'Authors', 'Series', 'ClassFrom', 'ClassTo', 'Subject', 'Program', 'Publisher',
                   'Description', 'Type', 'File1', 'File2', 'TypeResource', 'IsOVZ', 'TypePayResurse', 'UrlResurse',
                   'PublicationLanguage']

        csv_writer.writerow(headers)

        for book in books:

            row = [
                book.image_name+'.'+book.image_type,
                book.name,
                book.authors,
                book.series,
                book.class_from,
                book.class_to if book.class_from != book.class_to else '',
                book.subject,
                book.program,
                book.publisher,
                book.description,
                book.type,
                '',
                '',
                book.type_resourse,
                book.is_ovz or False,
                book.type_pay_resourse,
                book.url,
                book.publication_language,
            ]


            csv_writer.writerow(row)

        csv_buffer.seek(0)
        return csv_buffer.getvalue()


    @staticmethod
    def _add_images_to_zip(zip_file: ZipFile, books: List[Book]):
        """Добавление изображений в ZIP архив"""
        for book in books:
            if book.image_url and book.id:
                image_data = BookService.get_book_image_data(book.id)
                if image_data:
                    image_filename = book.image_name+'.'+book.image_type
                    zip_file.writestr(image_filename, image_data)