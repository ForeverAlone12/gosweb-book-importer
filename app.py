import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_bootstrap import Bootstrap5

from models import BookCharacteristick
from scraper import Scraper
from dotenv import load_dotenv

from api import api_bp
from services import BookService, ExportService

load_dotenv()

app = Flask(__name__)
Bootstrap5(app)

# Регистрируем API blueprint
app.register_blueprint(api_bp)

@app.route('/')
def index():
    books = BookService.get_all_books()
    subjects = list(set(book.subject for book in books if book.subject))
    classes = list(set(book.class_from for book in books if book.class_from))
    return render_template('index.html', books=books, subjects=subjects, classes=classes)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return redirect(url_for('index'))

    scraper = Scraper()

    # Используем Selenium для скрапинга
    scraped_data = scraper.scrape_with_selenium(url)

    # Создаем или обновляем книгу
    book = BookService.create_or_update_book(scraped_data)

    # Если в scraped_data есть URL изображения, скачиваем и сохраняем его
    image_url = scraped_data.get(BookCharacteristick.IMAGE_SRC)
    if image_url and book:
        BookService.download_and_save_image(image_url, book.id)

    return redirect(url_for('index'))

@app.route('/refresh-book', methods=['POST'])
def refresh_book():
    """Обновление данных книги с сайта"""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})

        scraper = Scraper()

        # Скрапим новые данные
        scraped_data = scraper.scrape_with_selenium(url)

        # Получаем существующую книгу
        existing_book = BookService.get_book_by_url(url)
        if not existing_book:
            return jsonify({'success': False, 'error': 'Книга не найдена'})

        # Обновляем характеристики
        BookService.update_book_characteristics(existing_book.id, scraped_data)

        # Обновляем изображение, если есть новое
        image_url = scraped_data.get('image_url') or scraped_data.get('cover_url')
        if image_url:
            BookService.download_and_save_image(image_url, existing_book.id)

        return jsonify({'success': True, 'message': 'Данные обновлены'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete', methods=['POST'])
def delete():
    try:
        book_id = request.form.get('book_id')
        success = BookService.delete_book(int(book_id))
        return json.dumps({'success': success})
    except Exception as e:
        return json.dumps({'error': str(e)}), 400

@app.route('/export-books', methods=['GET'])
def export_books():
    """Экспорт всех книг в ZIP архив с CSV и изображениями"""
    try:
        books = BookService.get_all_books()
        if not books:
            return jsonify({'error': 'Нет книг для экспорта'}), 404

        zip_buffer = ExportService.export_books_to_zip(books)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'books_export_{timestamp}.zip'

        # Отправляем ZIP архив
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export-book/<int:book_id>', methods=['GET'])
def export_book(book_id):
    """Экспорт одной книги в ZIP архив"""
    try:
        book = BookService.get_book_with_image(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        zip_buffer = ExportService.export_books_to_zip([book])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'book_{book_id}_export_{timestamp}.zip'

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)