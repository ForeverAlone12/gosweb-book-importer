# Выборка данных об учебнике с сайта издательства Просевщение

Данная программа помогать собрать данные об ученибке с издательства Просвещения по ссылке 
и сформировать архив для загрузки на платформу ГосВеб.


## Функционал
- Собирает данные об учебнике по ссылке с издательства просвещения.
- Данные об учебнике сохраняются в БД sqlite.
- Экспорт данных для загрузки на ГосВеб.


## В разработке
- Ассинхронная обработка
- автоматический выбор нужного браузера, пока используется Chrome. 
- Обработка ошибок

## Вспомогательные библиотеки
- [Bootstrap Flask](https://bootstrap-flask.readthedocs.io/en/stable/)

## Системные требования
Python3
Браузер Chrome


## Разработка

### For Windows:
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### For Linux:
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Миграции БД
#### Инициализация миграций (запускать единожды)
```shell
flask db init
```

#### Создаем миграцию
```shell
flask db migrate -m "change column type"
```

#### Применение миграции к базе данных
```shell
flask db upgrade
```

# Просмотр текущей миграции
```shell
flask db current
```

# Просмотр истории миграций
```shell
flask db history
```

# Откат последней миграции
```shell
flask db downgrade
```

# Откат к конкретной миграции
```shell
flask db downgrade <revision_id>
```

### Зафиксировать библиотеки
```shell
pip freeze > requirements.txt
```