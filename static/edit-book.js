// Обработчик открытия модального окна
$('.view-btn').click(function() {
    const bookId = $(this).data('id');
    loadBookData(bookId);

// Загрузка данных книги в модальное окно
function loadBookData(bookId) {
    $.ajax({
        url: '/api/books/' + bookId,
        method: 'GET',
        success: function(book) {
            $('#modalBookId').val(book.id);
            $('#modalBookUrl').val(book.url);
            $('#modalBookUrlDisplay').val(book.url);
            $('#modalBookImageUrl').val(book.image_url || '');

            // Устанавливаем изображение
            if (book.image_url) {
                $('#modalBookImage').attr('src', book.image_url).show();
            } else {
                $('#modalBookImage').hide();
            }

            // Очищаем контейнер характеристик
            $('.characteristics-container').empty();

            // Добавляем характеристики в форму
            if (book.characteristics) {
                Object.entries(book.characteristics).forEach(([key, value]) => {
                    if (key !== 'image_url') { // Пропускаем image_url, т.к. он уже есть
                        const inputId = `char_${key}`;
                        const field = `
                            <div class="mb-3">
                                <label class="form-label">${key.replace(/_/g, ' ').toUpperCase()}</label>
                                <input type="text" class="form-control"
                                       id="${inputId}"
                                       name="characteristics[${key}]"
                                       value="${value || ''}">
                            </div>
                        `;
                        $('.characteristics-container').append(field);
                    }
                });
            }
        },
        error: function() {
            alert('Ошибка при загрузке данных книги');
        }
    });
}

// Сохранение изменений
$('#saveBookChanges').click(function() {
    const bookId = $('#modalBookId').val();
    const formData = new FormData(document.getElementById('bookForm'));
    const characteristics = {};
    if (confirm('Экспортировать эту книгу в ZIP архив?')) {
        window.location.href = '/export-book/' + bookId;
    }
});

    // Собираем характеристики из формы
    formData.forEach((value, key) => {
        if (key.startsWith('characteristics[')) {
            const charKey = key.match(/\[(.*?)\]/)[1];
            characteristics[charKey] = value;
        }
    });

    // Добавляем image_url в характеристики
    characteristics.image_url = $('#modalBookImageUrl').val();

    const data = {
        characteristics: characteristics
    };

    $.ajax({
        url: '/api/books/' + bookId,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function() {
            alert('Изменения сохранены успешно!');
            $('#bookModal').modal('hide');
            location.reload(); // Перезагружаем страницу для обновления данных
        },
        error: function() {
            alert('Ошибка при сохранении изменений');
        }
    });
});

// Обновление данных с сайта
$('#refreshBookData').click(function() {
    const bookUrl = $('#modalBookUrl').val();
    if (!bookUrl) {
        alert('URL книги не найден');
        return;
    }

    if (!confirm('Вы уверены, что хотите обновить данные с сайта? Текущие изменения будут потеряны.')) {
        return;
    }

    $.ajax({
        url: '/refresh-book',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ url: bookUrl }),
        success: function(response) {
            if (response.success) {
                alert('Данные успешно обновлены с сайта!');
                $('#bookModal').modal('hide');
                location.reload();
            } else {
                alert('Ошибка при обновлении: ' + response.error);
            }
        },
        error: function() {
            alert('Ошибка при обновлении данных');
        }
    });
});