from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re
import base64
from transliterate import translit

@dataclass
class Book:
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

    id: Optional[int] = None
    url: Optional[str] = None
    name: Optional[str] = None
    authors: Optional[str] = None
    series: Optional[str] = None
    class_from: Optional[int] = None
    class_to: Optional[int] = None
    subject: Optional[str] = None
    program: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    part: Optional[int] = None
    type: Optional[str] = None
    type_resourse: Optional[str] = None
    is_ovz: Optional[bool] = False
    type_pay_resourse: Optional[str] = None
    publication_language: Optional[str] = None
    image_name: Optional[str] = None
    image_data: Optional[bytes] = None
    image_url: Optional[str] = None
    image_type: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self, include_image: bool = False) -> Dict[str, Any]:
        """Конвертирует объект книги в словарь"""
        result = {
            'id': self.id,
            'url': self.url,
            'name': self.name,
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
            'is_ovz' : self.is_ovz or False,
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
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
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
    NAME = 'Название',
    SERIES = 'Линия УМК, серия',
    DESCRIPTION = 'Описание',
    SUBJECT = 'Предмет',
    PUBLISHER = 'Издательство',
    TYPE = 'Вид литературы',
    PUBLICATION_LANGUAGE = 'Язык',
    CLASSES = 'Класс, возраст',
    PROGRAM = 'Уровень образования',
    PART = 'Часть',
    AUTHORS = 'Авторы',
    IMAGE_SRC = 'image_src'