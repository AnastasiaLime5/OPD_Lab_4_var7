import os
import unittest
from app import app, read_users, add_user


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['USERS_FILE'] = 'test_users.txt'
        app.config['PASSWORD_MIN_LENGTH'] = 6
        self.app = app.test_client()
        with open(app.config['USERS_FILE'], 'w', encoding='utf-8') as f:
            f.write('')

    def tearDown(self):
        if os.path.exists(app.config['USERS_FILE']):
            os.remove(app.config['USERS_FILE'])

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вход', response.data.decode('utf-8'))

    def test_successful_registration(self):
        response = self.app.post('/register', data={
            'username': 'test@user!123',
            'password': 'password!@#',
            'confirm_password': 'password!@#'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Добро пожаловать, test@user!123', response.data.decode('utf-8'))

        users = read_users()
        self.assertIn('test@user!123', users)
        self.assertEqual(users['test@user!123'], 'password!@#')  # Пароль хранится открыто

    def test_registration_password_mismatch(self):
        response = self.app.post('/register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'different123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Пароли не совпадают', response.data.decode('utf-8'))

    def test_registration_existing_user(self):
        self.app.post('/register', data={
            'username': 'user@domain.com',
            'password': 'P@ssw0rd!',
            'confirm_password': 'P@ssw0rd!'
        })

        response = self.app.post('/register', data={
            'username': 'user@domain.com',
            'password': 'NewP@ss1',
            'confirm_password': 'NewP@ss1'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Пользователь уже существует', response.data.decode('utf-8'))

    def test_registration_short_password(self):
        response = self.app.post('/register', data={
            'username': 'testuser',
            'password': '12345',
            'confirm_password': '12345'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Пароль должен содержать более {app.config["PASSWORD_MIN_LENGTH"]} символов',
                     response.data.decode('utf-8'))

    def test_special_chars_in_username_and_password(self):
        response = self.app.post('/register', data={
            'username': 'admin@site.com:8080',
            'password': '!@#$%^&*()',
            'confirm_password': '!@#$%^&*()'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Добро пожаловать, admin@site.com:8080', response.data.decode('utf-8'))

    def test_successful_login(self):
        self.app.post('/register', data={
            'username': 'user:name',
            'password': 'pass:word',
            'confirm_password': 'pass:word'
        })

        self.app.get('/logout')

        response = self.app.post('/login', data={
            'username': 'user:name',
            'password': 'pass:word'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)


    def test_failed_login(self):
        response = self.app.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Неверный логин или пароль', response.data.decode('utf-8'))

    def test_unauthorized_access(self):
        response = self.app.get('/welcome')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_logout(self):
        self.app.post('/register', data={
            'username': 'testuser',
            'password': 'testpass',
            'confirm_password': 'testpass'
        })

        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вход', response.data.decode('utf-8'))  # Проверяем что вернулись на страницу входа

    def test_read_users_empty_file(self):
        users = read_users()
        self.assertEqual(users, {})

    def test_add_user(self):
        add_user('direct_test', 'direct_password')
        users = read_users()
        self.assertEqual(users['direct_test'], 'direct_password')


if __name__ == '__main__':
    unittest.main()