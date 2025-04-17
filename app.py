import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['USERS_FILE'] = 'users.txt'
app.config['PASSWORD_MIN_LENGTH'] = 6


def read_users():
    users = {}
    try:
        with open(app.config['USERS_FILE'], 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        username, password = line.split(':', 1)
                        users[username] = password
                    except ValueError:
                        continue
    except FileNotFoundError:
        pass
    return users


def add_user(username, password):
    if len(password) <= app.config['PASSWORD_MIN_LENGTH']:
        raise ValueError(f"Пароль должен содержать более {app.config['PASSWORD_MIN_LENGTH']} символов")

    with open(app.config['USERS_FILE'], 'a', encoding='utf-8') as file:
        file.write(f"{username}:{password}\n")


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = read_users()

        if not username or not password:
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('login.html')

        if username not in users:
            flash('Неверный логин или пароль', 'error')
            return render_template('login.html')

        if users[username] != password:  # Прямое сравнение паролей
            flash('Неверный логин или пароль', 'error')
            return render_template('login.html')

        session['username'] = username
        return redirect(url_for('welcome'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password or not confirm_password:
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        if len(password) <= app.config['PASSWORD_MIN_LENGTH']:
            flash(f'Пароль должен содержать более {app.config["PASSWORD_MIN_LENGTH"]} символов', 'error')
            return render_template('register.html')

        users = read_users()
        if username in users:
            flash('Пользователь уже существует', 'error')
            return render_template('register.html')

        try:
            add_user(username, password)  # Сохраняем пароль как есть
            session['username'] = username
            return redirect(url_for('welcome'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    if not os.path.exists(app.config['USERS_FILE']):
        open(app.config['USERS_FILE'], 'w').close()
    app.run(debug=True)