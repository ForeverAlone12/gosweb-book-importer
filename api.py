from flask import Blueprint, request, jsonify, send_file

from io import BytesIO
import base64
from services import BookService

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/books', methods=['GET'])
def get_books():
    """Получение списка всех книг (без данных изображений)"""
    books = BookService.get_all_books()
    return jsonify([book.to_dict(include_image=False) for book in books])

@api_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    """Получение конкретной книги по ID"""
    book = BookService.get_book_with_image(book_id)
    if book:
        return jsonify(book.to_dict(include_image=True))
    return jsonify({'error': 'Book not found'}), 404

@api_bp.route('/books/<int:book_id>/image', methods=['GET'])
def get_book_image(book_id: int):
    """Получение изображения книги как файл"""
    image_data = BookService.get_book_image_data(book_id)
    if image_data:
        book = BookService.get_book(book_id)
        return send_file(
            BytesIO(image_data),
            mimetype=f"image/{book.image_type}" if book and book.image_type else 'image/jpeg',
            as_attachment=False
        )
    return jsonify({'error': 'Image not found'}), 404

@api_bp.route('/books/<int:book_id>/image', methods=['POST'])
def set_book_image(book_id: int):
    """Установка изображения для книги"""
    try:
        if 'image' in request.files:
            # Загрузка файла
            image_file = request.files['image']
            image_data = image_file.read()
            image_type = image_file.content_type

            success = BookService.update_book_image(book_id, image_data, None, image_type)
            if success:
                return jsonify({'message': 'Image updated successfully'}), 200

        elif request.is_json:
            # Загрузка через JSON (base64 или URL)
            data = request.get_json()

            if data.get('image_data_base64'):
                # Base64 encoded image
                image_data = base64.b64decode(data['image_data_base64'])
                image_type = data.get('image_type', 'image/jpeg')

                success = BookService.update_book_image(book_id, image_data, data.get('image_url'), image_type)
                if success:
                    return jsonify({'message': 'Image updated successfully'}), 200

            elif data.get('image_url'):
                # Скачивание по URL
                success = BookService.download_and_save_image(data['image_url'], book_id)
                if success:
                    return jsonify({'message': 'Image downloaded and saved successfully'}), 200
                else:
                    return jsonify({'error': 'Failed to download image'}), 400

        return jsonify({'error': 'No image data provided'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/books/<int:book_id>/image', methods=['DELETE'])
def delete_book_image(book_id: int):
    """Удаление изображения книги"""
    success = BookService.update_book_image(book_id, None, None, None)
    if success:
        return jsonify({'message': 'Image deleted successfully'})
    return jsonify({'error': 'Book not found'}), 404

@api_bp.route('/books/exists/<path:url>', methods=['GET'])
def check_book_exists(url: str):
    """Проверка существования книги по URL"""
    exists = BookService.book_exists(url)
    return jsonify({'exists': exists, 'url': url})

@api_bp.route('/books/search', methods=['GET'])
def search_books():
    """Поиск книг по URL и характеристикам"""
    query = request.args.get('q', '')
    search_in_chars = request.args.get('search_chars', 'true').lower() == 'true'

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    books = BookService.search_books(query, search_in_chars)
    return jsonify([book.to_dict() for book in books])

@api_bp.route('/books/characteristics/<key>', methods=['GET'])
def get_books_by_characteristic(key: str):
    """Получение книг по конкретной характеристике"""
    value = request.args.get('value')
    if not value:
        return jsonify({'error': 'Value parameter is required'}), 400

    books = BookService.get_books_by_characteristic(key, value)
    return jsonify([book.to_dict() for book in books])

@api_bp.route('/books/characteristics/<key>/values', methods=['GET'])
def get_characteristic_values(key: str):
    """Получение уникальных значений для конкретной характеристики"""
    values = BookService.get_unique_characteristic_values(key)
    return jsonify({'characteristic': key, 'values': values})

@api_bp.route('/books/stats', methods=['GET'])
def get_stats():
    """Получение статистики по книгам"""
    books = BookService.get_all_books()

    # Собираем статистику по характеристикам
    characteristics_stats = {}
    for book in books:
        if book.characteristics:
            for key, value in book.characteristics.items():
                if key not in characteristics_stats:
                    characteristics_stats[key] = {
                        'count': 0,
                        'unique_values': set(),
                        'type': type(value).__name__
                    }
                characteristics_stats[key]['count'] += 1
                characteristics_stats[key]['unique_values'].add(str(value))

    # Преобразуем sets в lists для JSON
    for key in characteristics_stats:
        characteristics_stats[key]['unique_values'] = list(characteristics_stats[key]['unique_values'])
        characteristics_stats[key]['unique_count'] = len(characteristics_stats[key]['unique_values'])

    stats = {
        'total_books': len(books),
        'books_with_characteristics': len([b for b in books if b.characteristics]),
        'total_characteristics_keys': len(characteristics_stats),
        'characteristics_stats': characteristics_stats
    }

    return jsonify(stats)


@api_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id: int):
    """Обновление книги"""
    try:
        update_data = request.get_json()

        book = BookService.get_book(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        # Обновляем характеристики
        if 'characteristics' in update_data:
            success = BookService.update_book_characteristics(
                book_id, update_data['characteristics']
            )
            if not success:
                return jsonify({'error': 'Failed to update book'}), 500

        # Обновляем изображение, если указано
        if 'image_url' in update_data.get('characteristics', {}):
            image_url = update_data['characteristics']['image_url']
            if image_url:
                BookService.download_and_save_image(image_url, book_id)

        return jsonify({'success': True, 'message': 'Book updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400