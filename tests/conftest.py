import pytest
import os
import sys
from unittest.mock import Mock, patch
from models import db as database
from app import app as flask_app


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='session')
def app():
    """Создает тестовое Flask приложение"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with flask_app.app_context():
        database.create_all()

    yield flask_app

    # Очистка после тестов
    with flask_app.app_context():
        database.drop_all()

@pytest.fixture
def db_session(app):
    """Сессия базы данных с автоматической очисткой"""
    with app.app_context():
        database.session.remove()
        database.drop_all()
        database.create_all()

        yield database

        database.session.rollback()


@pytest.fixture
def sample_book_data():
    """Фикстура с тестовыми данными книги"""
    return {
        'url': 'https://example.com/book/1',
        'name': 'Test Book',
        'authors': 'Author One, Author Two',
        'series': 'Test Series',
        'program': 'Basic Education',
        'publisher': 'Test Publisher',
        'description': 'Test description of the book',
        'class_level': '5',
        'publication_language': 'Russian',
        'characteristics': {
            'isbn': '123-456-789',
            'pages': '200',
            'year': '2023'
        }
    }


@pytest.fixture
def mock_selenium():
    """Мок для Selenium"""
    with patch('selenium.webdriver.Chrome') as mock_chrome:
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver.title = 'Test Page Title'
        mock_driver.page_source = '<html><body>Test content</body></html>'
        mock_driver.execute_script.return_value = None
        mock_driver.quit.return_value = None

        yield mock_driver