# test_controllers.py
import unittest
from unittest.mock import Mock, call
from controllers.currencycontroller import CurrencyController
from controllers.usercontroller import UserController


class TestCurrencyController(unittest.TestCase):

    def setUp(self):
        # Создаем Mock-объект, который будет имитировать DatabaseController
        self.mock_db = Mock()
        self.controller = CurrencyController(self.mock_db)

    def test_create_currency(self):
        # Настраиваем mock_db.execute, чтобы возвращал ID новой строки
        self.mock_db.execute.return_value = 5

        currency_id = self.controller.create_currency(
            '980', 'UAH', 'Украинская гривна', 2.30, 1
        )

        self.assertEqual(currency_id, 5)
        # Проверяем, что execute был вызван с корректными параметрами
        self.mock_db.execute.assert_called_once_with(
            unittest.mock.ANY,  # Ожидаем любой запрос (ANY)
            ('980', 'UAH', 'Украинская гривна', 2.30, 1),
            commit=True
        )

    def test_get_currency_found(self):
        # Имитируем возвращаемое значение метода fetch_one
        mock_row = {'id': 1, 'char_code': 'USD', 'name': 'Доллар', 'value': 90.0, 'nominal': 1, 'num_code': '840'}
        self.mock_db.execute.return_value = mock_row

        currency = self.controller.get_currency(1)

        self.assertEqual(currency, mock_row)
        self.mock_db.execute.assert_called_once_with(
            unittest.mock.ANY,
            (1,),
            fetch_one=True
        )

    def test_update_currency(self):
        # Имитируем, что обновление затронуло 1 строку
        self.mock_db.cursor.rowcount = 1

        success = self.controller.update_currency(
            2,
            char_code='EUR_new',
            value=77.0
        )

        self.assertTrue(success)
        # Проверяем, что SQL-запрос был сформирован корректно
        self.mock_db.execute.assert_called_once_with(
            "UPDATE currencies SET char_code = ?, value = ? WHERE id = ?",
            ['EUR_new', 77.0, 2],
            commit=True
        )

    def test_delete_currency(self):
        # Имитируем, что удаление затронуло 1 строку
        self.mock_db.cursor.rowcount = 1

        success = self.controller.delete_currency(1)

        self.assertTrue(success)
        self.mock_db.execute.assert_called_once_with(
            unittest.mock.ANY,
            (1,),
            commit=True
        )


class TestUserController(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.controller = UserController(self.mock_db)

    def test_create_user(self):
        self.mock_db.execute.return_value = 10

        user_id = self.controller.create_user('Петр Петрович')

        self.assertEqual(user_id, 10)
        self.mock_db.execute.assert_called_once_with(
            unittest.mock.ANY,
            ('Петр Петрович',),
            commit=True
        )

    def test_list_users(self):
        # Имитируем возвращаемые строки
        mock_rows = [{'id': 1, 'name': 'Иван'}, {'id': 2, 'name': 'Сергей'}]
        self.mock_db.execute.return_value = mock_rows

        users = self.controller.list_users()

        self.assertEqual(users, mock_rows)
        self.mock_db.execute.assert_called_once_with(
            unittest.mock.ANY,
            fetch_all=True
        )


if __name__ == '__main__':
    # Для запуска тестов выполните: python -m unittest test_controllers.py
    unittest.main()