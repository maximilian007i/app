from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import requests
import pandas as pd
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# Имя файла для хранения заметок
notes_file = 'notes.csv'

# Пользовательские данные для авторизации
users = {
    'user1': 'password1',
    'user2': 'password2'
}

# Инициализация CSV-файла
def initialize_csv():
    if not os.path.exists(notes_file):
        df = pd.DataFrame(columns=['username', 'note'])
        df.to_csv(notes_file, index=False)

# Функция для сохранения заметки в CSV
def save_note_to_csv(username, note):
    df = pd.read_csv(notes_file)
    new_note = pd.DataFrame({'username': [username], 'note': [note]})
    df = pd.concat([df, new_note], ignore_index=True)
    df.to_csv(notes_file, index=False)

# Функция для получения заметок пользователя из CSV
def get_notes_from_csv(username):
    df = pd.read_csv(notes_file)
    user_notes = df[df['username'] == username]
    return user_notes['note'].tolist()

# Функция для проверки орфографии с использованием Яндекс.Спеллера
def check_spelling(note):
    response = requests.get("https://speller.yandex.net/services/spellservice.json/checkText", params={'text': note})
    result = response.json()
    return result

# Авторизация пользователя
@auth.get_password
def get_password(username):
    if username in users:
        return users.get(username)
    return None

# Маршрут для добавления заметки
@app.route('/notes', methods=['POST'])
@auth.login_required
def add_note():
    data = request.json
    note = data.get('note')
    if not note:
        return jsonify({'error': 'No note provided'}), 400

    # Проверка орфографии
    spelling_errors = check_spelling(note)
    if spelling_errors:
        return jsonify({'error': 'Spelling errors found', 'errors': spelling_errors}), 400

    # Сохраняем заметку
    save_note_to_csv(auth.current_user(), note)
    return jsonify({'message': 'Note added successfully'}), 201

# Маршрут для получения списка заметок
@app.route('/notes', methods=['GET'])
@auth.login_required
def get_notes():
    notes = get_notes_from_csv(auth.current_user())
    return jsonify({'notes': notes}), 200

# Запускаем приложение
if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True)