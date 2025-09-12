from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re
import base64

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from transliterate import translit


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class BookBase(db.Model):
    """Данные учебника.

    Attributes:
        id: Идентификатор учебника в системе
        url: Ссылка на учебник
        name: Название учебника
        authors: Авторы учебника
        series: Серия
        class_from: Класс (начальный)
        class_to: Класс (конечный)
        subject: Предмет
        program: Программа
        publisher: Издательство
        description: Описание
        part: Часть
        type: Вид материала
        type_resourse: Тип ресурса
        is_ovz: Для ОВЗ
        type_pay_resourse: Тип стоимости ресурса (Бесплатно|По подписке)
        publication_language: Язык издания
        image_name: Названия файла с обложкой при сохранении
        image_data: Файл с обложкой в формате base64
        image_url: Ссылка на обложку учебника
        image_type: Расширение файла обложки
        created_at: Дата создания информации
    """
    __tablename__ = "books"

    id: Mapped[Optional[int]] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    url: Mapped[Optional[str]] = mapped_column(db.Text)
    name: Mapped[Optional[str]] = mapped_column(db.Text, nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(db.Text, nullable=False)
    series: Mapped[Optional[str]] = mapped_column(db.Text)
    class_from: Mapped[Optional[int]] = mapped_column(db.Integer)
    class_to: Mapped[Optional[int]] = mapped_column(db.Integer)
    subject: Mapped[Optional[str]] = mapped_column(db.Text)
    program: Mapped[Optional[str]] = mapped_column(db.Text)
    publisher: Mapped[Optional[str]] = mapped_column(db.Text)
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    part: Mapped[Optional[int]] = mapped_column(db.Integer)
    type: Mapped[Optional[str]] = mapped_column(db.Text)
    type_resourse: Mapped[Optional[str]] = mapped_column(db.Text)
    is_ovz: Mapped[Optional[bool]] = mapped_column(db.Boolean, default=False)
    type_pay_resourse: Mapped[Optional[str]] = mapped_column(db.Text)
    publication_language: Mapped[Optional[str]] = mapped_column(db.Text)
    image_name: Mapped[Optional[str]] = mapped_column(db.Text)
    image_data: Mapped[Optional[bytes]] = mapped_column(db.LargeBinary)
    image_url: Mapped[Optional[str]] = mapped_column(db.Text)
    image_type: Mapped[Optional[str]] = mapped_column(db.Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, default=datetime.now)

    # Индексы
    __table_args__ = (
        Index('books_url_idx', 'url'),
        Index('books_authors_idx', 'authors'),
        Index('books_series_idx', 'series'),
        Index('books_class_from_idx', 'class_from'),
        Index('books_class_from_class_to_idx', 'class_from', 'class_to'),
        Index('books_part_idx', 'part'),
        Index('books_program_idx', 'program'),
        Index('books_publisher_idx', 'publisher'),
        Index('books_series_idx', 'series'),
        Index('books_subject_idx', 'subject'),
    )

    def to_dict(self, include_image: bool = False) -> Dict[str, Any]:
        """Конвертирует объект книги в словарь"""
        result = {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'authors': self.authors,
            'series': self.series or '',
            'class_from': self.class_from,
            'class_to': self.class_to if self.class_from != self.class_to else '',
            'subject': self.subject,
            'program': self.program or '',
            'publisher': self.publisher or '',
            'description': self.description,
            'part': self.part or '',
            'type': self.type or '',
            'type_resourse': self.type_resourse or '',
            'is_ovz': self.is_ovz or False,
            'type_pay_resourse': self.type_pay_resourse or '',
            'publication_language': self.publication_language or '',
            'image_name': self.image_name,
            'image_data': self.image_data,
            'image_url': self.image_url,
            'image_type': self.image_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_image and self.image_data:
            result['image_data_base64'] = base64.b64encode(self.image_data).decode('utf-8')

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookBase':
        """Создает объект книги из данных."""

        image_data = base64.b64decode(data['image_data_base64']) if data.get('image_data_base64') else None

        print(f"data: {data}")  
        print(f"data[class]: {data[BookCharacteristick.CLASSES]}")  

        numbers_class = re.findall(r"\d+", data.get(BookCharacteristick.CLASSES))        
        class_from=min(numbers_class)
        class_to=max(numbers_class)
        
        subject = data.get(BookCharacteristick.SUBJECT)
        subject = re.sub(r'[ьъ]', '', subject)
        part = data.get(BookCharacteristick.PART)
        image_name=translit(subject, reversed=True)
        image_name=re.sub(r'\s+', '_', image_name)
        image_name = "_".join([image_name, str(class_from), str(part)])


        return cls(
            id=data.get('id'),
            url=data.get('url'),
            name=data.get(BookCharacteristick.NAME),
            series=data.get(BookCharacteristick.SERIES),
            class_from=class_from,
            class_to=class_to,
            authors=data.get(BookCharacteristick.AUTHORS),
            subject=data.get(BookCharacteristick.SUBJECT),
            program=data.get(BookCharacteristick.PROGRAM),
            publisher=data.get(BookCharacteristick.PUBLISHER),
            description=data.get(BookCharacteristick.DESCRIPTION),
            part=data.get(BookCharacteristick.PART),
            type=data.get(BookCharacteristick.TYPE),
            type_resourse=data.get('type_resourse') or '',
            is_ovz=data.get('is_ovz') or False,
            type_pay_resourse=data.get('type_pay_resourse') or '',
            publication_language=data.get(BookCharacteristick.PUBLICATION_LANGUAGE) or '',
            image_name=image_name,
            image_data=image_data,
            image_url=data.get('image_src'),
            image_type=data.get('image_type'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

    def get_characteristic(self, key: str, default: Any = None) -> Any:
        """Получение конкретной характеристики"""
        return self.characteristics.get(key, default) if self.characteristics else default

    def set_characteristic(self, key: str, value: Any):
        """Установка характеристики"""
        if self.characteristics is None:
            self.characteristics = {}
        self.characteristics[key] = value


    def set_image(self, image_data: bytes, image_url: str = None, image_type: str = None):
        """Установка изображения книги"""
        self.image_data = image_data
        self.image_url = image_url
        self.image_type = image_type


class BookCharacteristick(str, Enum):
    NAME = 'Название'
    SERIES = 'Линия УМК, серия'
    DESCRIPTION = 'Описание'
    SUBJECT = 'Предмет'
    PUBLISHER = 'Издательство'
    TYPE = 'Вид литературы'
    PUBLICATION_LANGUAGE = 'Язык'
    CLASSES = 'Класс, возраст'
    PROGRAM = 'Уровень образования'
    PART = 'Часть'
    AUTHORS = 'Авторы'
    IMAGE_SRC = 'image_src'