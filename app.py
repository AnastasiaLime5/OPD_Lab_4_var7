from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)                             # Создание экземпляра Flask-приложения
app.secret_key = 'secret_key'                     # Установка секретного ключа для подписи сессий
app.config['USERS_FILE'] = 'users.txt'            # Настройка пути к файлу с пользователями

def read_users():                                 # Функция для чтения пользователей из файла
    users = {}                                    # Создание пустого словаря для пользователей
    try:
        with open(app.config['USERS_FILE'], 'r') as file:  # Открытие файла для чтения
            for line in file:                     # Чтение файла построчно
                username, password = line.strip().split(':')  # Разделение строки на логин и пароль
                users[username] = password        # Добавление пары в словарь
    except FileNotFoundError:                     # Обработка отсутствия файла
        pass                                      # Пропуск ошибки
    return users                                  # Возврат словаря пользователей

def add_user(username, password):                 # Функция добавления нового пользователя
    with open(app.config['USERS_FILE'], 'a') as file:  # Открытие файла для дозаписи
        file.write(f"{username}:{password}\n")    # Запись данных пользователя

@app.route('/')                                   # Декоратор маршрута для главной страницы
def home():                                       # Функция обработки главной страницы
    if 'username' in session:                     # Проверка авторизации пользователя
        return redirect(url_for('welcome'))       # Перенаправление авторизованного пользователя
    return redirect(url_for('login'))             # Перенаправление неавторизованного пользователя

@app.route('/login', methods=['GET', 'POST'])     # Маршрут для страницы входа
def login():                                      # Функция обработки входа
    if request.method == 'POST':                  # Обработка POST-запроса (отправка формы)
        username = request.form.get('username')   # Получение логина из формы
        password = request.form.get('password')   # Получение пароля из формы
        users = read_users()                      # Загрузка списка пользователей

        if username in users and users[username] == password:  # Проверка учетных данных
            session['username'] = username        # Сохранение логина в сессии
            return redirect(url_for('welcome'))   # Перенаправление при успешном входе
        else:
            return render_template('login.html',   # Возврат формы с ошибкой
                                error="Неверный логин или пароль")
    return render_template('login.html')          # Отображение формы входа (GET-запрос)

@app.route('/register', methods=['GET', 'POST'])  # Маршрут для страницы регистрации
def register():                                   # Функция обработки регистрации
    if request.method == 'POST':                  # Обработка POST-запроса
        username = request.form.get('username')   # Получение данных из формы
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        users = read_users()                      # Загрузка списка пользователей

        if not username or not password or not confirm_password:  # Проверка заполнения полей
            return render_template('register.html',
                                error="Все поля обязательны для заполнения")
        if password != confirm_password:         # Проверка совпадения паролей
            return render_template('register.html',
                                error="Пароли не совпадают")
        if username in users:                    # Проверка существования пользователя
            return render_template('register.html',
                                error="Пользователь уже существует")

        add_user(username, password)             # Добавление нового пользователя
        session['username'] = username           # Сохранение в сессии
        return redirect(url_for('welcome'))      # Перенаправление после регистрации
    return render_template('register.html')      # Отображение формы регистрации (GET)

@app.route('/welcome')                           # Маршрут для защищенной страницы
def welcome():                                   # Функция приветствия
    if 'username' not in session:                # Проверка авторизации
        return redirect(url_for('login'))        # Перенаправление если не авторизован
    return render_template('welcome.html',      # Отображение страницы приветствия
                         username=session['username'])

@app.route('/logout')                            # Маршрут для выхода из системы
def logout():                                    # Функция выхода
    session.pop('username', None)                # Удаление данных пользователя из сессии
    return redirect(url_for('login'))            # Перенаправление на страницу входа

if __name__ == '__main__':
    app.run(debug=True)