import os
import unittest
from app import app, read_users, add_user


class FlaskTestCase(unittest.TestCase):  # Класс для тестирования Flask-приложения

    def setUp(self):  # Метод подготовки перед каждым тестом
        app.config['TESTING'] = True  # Включение тестового режима Flask
        app.config['WTF_CSRF_ENABLED'] = False  # Отключение CSRF-защиты для тестов
        app.config['USERS_FILE'] = 'test_users.txt'  # Использование тестового файла пользователей
        self.app = app.test_client()  # Создание тестового клиента
        with open(app.config['USERS_FILE'], 'w') as f:  # Очистка тестового файла
            f.write('')

    def tearDown(self):  # Метод очистки после каждого теста
        if os.path.exists(app.config['USERS_FILE']):  # Проверка существования файла
            os.remove(app.config['USERS_FILE'])  # Удаление тестового файла

    def test_index(self):  # Тест главной страницы
        response = self.app.get('/')  # Отправка GET-запроса на главную
        self.assertEqual(response.status_code, 302)  # Проверка редиректа (код 302)
        self.assertIn('/login', response.location)  # Проверка перенаправления на /login

    def test_login_page(self):  # Тест страницы входа
        response = self.app.get('/login')  # Запрос страницы входа
        self.assertEqual(response.status_code, 200)  # Проверка успешного ответа
        self.assertIn('Вход в систему', response.data.decode('utf-8'))  # Проверка содержимого

    def test_successful_registration(self):  # Тест успешной регистрации
        response = self.app.post('/register', data={  # Отправка данных регистрации
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'testpass'
        }, follow_redirects=True)  # Следование за редиректом

        self.assertEqual(response.status_code, 200)  # Проверка успешного ответа
        self.assertIn('Добро пожаловать', response.data.decode('utf-8'))  # Проверка приветствия

        users = read_users()  # Чтение пользователей из файла
        self.assertIn('testuser', users)  # Проверка наличия пользователя
        self.assertEqual(users['testuser'], 'testpass')  # Проверка корректности пароля

    def test_registration_password_mismatch(self):  # Тест несовпадения паролей
        response = self.app.post('/register', data={
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'wrongpass'  # Преднамеренная ошибка в подтверждении
        })

        self.assertEqual(response.status_code, 200)  # Проверка ответа
        self.assertIn('Пароли не совпадают', response.data.decode('utf-8'))  # Проверка ошибки

    def test_registration_existing_user(self):  # Тест регистрации существующего пользователя
        self.app.post('/register', data={  # Сначала регистрируем пользователя
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'testpass'
        })

        response = self.app.post('/register', data={  # Пытаемся зарегистрировать повторно
            'username': 'testuser',  # Тот же логин
            'password': 'newpass',
            'confirm_password': 'newpass'
        })

        self.assertEqual(response.status_code, 200)  # Проверка ответа
        self.assertIn('Пользователь уже существует', response.data.decode('utf-8'))  # Проверка ошибки

    def test_successful_login(self):  # Тест успешного входа
        self.app.post('/register', data={  # Сначала регистрация
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'testpass'
        })

        self.app.get('/logout')  # Выход из системы

        response = self.app.post('/login', data={  # Попытка входа
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Проверка успешного входа
        self.assertIn('Добро пожаловать', response.data.decode('utf-8'))  # Проверка приветствия

    def test_failed_login(self):  # Тест неудачного входа
        response = self.app.post('/login', data={
            'username': 'wronguser',  # Несуществующий пользователь
            'password': 'wrongpass'  # Неверный пароль
        })

        self.assertEqual(response.status_code, 200)  # Проверка ответа
        self.assertIn('Неверный логин или пароль', response.data.decode('utf-8'))  # Проверка ошибки

    def test_unauthorized_access(self):  # Тест неавторизованного доступа
        response = self.app.get('/welcome')  # Попытка доступа без авторизации
        self.assertEqual(response.status_code, 302)  # Проверка редиректа
        self.assertIn('/login', response.location)  # Проверка перенаправления на вход

    def test_logout(self):  # Тест выхода из системы
        self.app.post('/register', data={  # Сначала регистрация и вход
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'testpass'
        })

        response = self.app.get('/logout', follow_redirects=True)  # Выход
        self.assertEqual(response.status_code, 200)  # Проверка успешного выхода
        self.assertIn('Вход в систему', response.data.decode('utf-8'))  # Проверка перенаправления


if __name__ == '__main__':
    unittest.main()