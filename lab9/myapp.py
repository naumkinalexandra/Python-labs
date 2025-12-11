from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import App, User, Currency, UserCurrency
from controllers.databasecontroller import DatabaseController
from controllers.currencycontroller import CurrencyController
from controllers.usercontroller import UserController
from controllers.usercurrencycontroller import UserCurrencyController
from utils.currencies_cbapi import get_currencies
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape()
)


main_app = App('Лабораторная работа № 9 (CRUD для отслеживания курсов валют)', '1.0.0')

# Инициализация базы данных и контроллеров
db_controller = DatabaseController()
currency_controller = CurrencyController(db_controller)
user_controller = UserController(db_controller)
user_currency_controller = UserCurrencyController(db_controller)

def init_test_data():
    """Инициализация данных в базе"""

    user_controller.create_user('Иван Сергеевич')
    user_controller.create_user('Сергей Иванович')
    user_controller.create_user('Владимир Владимирович Пу')
    user_controller.create_user('Варя')

    currency_controller.create_currency('156', 'CNY', 'Китайский юань', 12.80, 1)
    currency_controller.create_currency('840', 'USD', 'Доллар США', 90.0000, 1)
    currency_controller.create_currency('978', 'EUR', 'Евро', 75.8520, 1)
    currency_controller.create_currency('826', 'GBP', 'Фунт', 95.0000, 1)


    user_currency_controller.create_user_currency(1, 1)  # Иван подписан на USD
    user_currency_controller.create_user_currency(1, 2)  # Иван подписан на EUR
    user_currency_controller.create_user_currency(2, 1)  # Сергей подписан на USD
    user_currency_controller.create_user_currency(3, 3)  # Владимир подписан на CNY
    user_currency_controller.create_user_currency(4, 1)  # Варя на все
    user_currency_controller.create_user_currency(4, 2)  # 
    user_currency_controller.create_user_currency(4, 3)  # 
    user_currency_controller.create_user_currency(4, 4)  # 

init_test_data()


def update_currency_rates():
    """Обновление курсов валют через API ЦБРФ"""
    try:
        currencies = currency_controller.list_currencies()
        currency_codes = [currency['char_code'] for currency in currencies]

        rates = get_currencies(currency_codes)

        currency_controller.update_currency_rates(rates)

        return True, "Курсы валют успешно обновлены"
    except Exception as e:
        return False, f"Ошибка обновления курсов валют: {str(e)}"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        try:
            if path == '/':
                self.handle_index()
            elif path == '/users':
                self.handle_users()
            elif path == '/user':
                user_id = query_params.get('id', [None])[0]
                if user_id:
                    self.handle_user(int(user_id))
                else:
                    self.send_error(400, "Missing user id parameter")
            elif path == '/currencies':
                self.handle_currencies()
            elif path == '/currency/delete':
                currency_id = query_params.get('id', [None])[0]
                if currency_id:
                    self.handle_delete_currency(int(currency_id))
                else:
                    self.send_error(400, "Missing currency id parameter")
            elif path == '/user/delete':
                user_id = query_params.get('id', [None])[0]
                if user_id:
                    self.handle_delete_user(int(user_id))
                else:
                    self.send_error(400, "Missing user id parameter")
            elif path == '/update-currencies':
                self.handle_update_currencies()
            else:
                self.send_error(404, "Page not found")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)

            if path == '/currency/create':
                self.handle_create_currency(form_data)
            elif path == '/currency/update':
                self.handle_update_currency(form_data)
            elif path == '/user/create':
                self.handle_create_user(form_data)
            elif path == '/user/update':
                self.handle_update_user(form_data)
            else:
                self.send_error(404, "Page not found")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

    def send_html_response(self, content):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def send_redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

    def handle_index(self):
        template = env.get_template("index.html")
        result = template.render(
            myapp="Лабораторная работа № 9 (CRUD для отслеживания курсов валют)",
            navigation=[
                {'caption': 'Пользователи', 'href': '/users'},
                {'caption': 'Валюты', 'href': '/currencies'},
            ]
        )
        self.send_html_response(result)

    def handle_users(self):
        users = user_controller.list_users()

        template = env.get_template("users.html")
        result = template.render(
            users=users,
            navigation=[
                {'caption': 'Главная', 'href': '/'},
                {'caption': 'Валюты', 'href': '/currencies'},
            ]
        )
        self.send_html_response(result)

    def handle_user(self, user_id):
        user = user_controller.get_user(user_id)
        if not user:
            self.send_error(404, "User not found")
            return

        user_currencies = user_currency_controller.get_user_currencies_detailed(user_id)

        template = env.get_template("user.html")
        result = template.render(
            user=user,
            currencies=user_currencies,
            navigation=[
                {'caption': 'Главная', 'href': '/'},
                {'caption': 'Пользователи', 'href': '/users'},
                {'caption': 'Валюты', 'href': '/currencies'},
            ]
        )
        self.send_html_response(result)

    def handle_currencies(self):
        currencies = currency_controller.list_currencies()

        template = env.get_template("currencies.html")
        result = template.render(
            currencies=currencies,
            navigation=[
                {'caption': 'Главная', 'href': '/'},
                {'caption': 'Пользователи', 'href': '/users'},
            ]
        )
        self.send_html_response(result)

    def handle_delete_currency(self, currency_id):
        """Удаление валюты"""
        success = currency_controller.delete_currency(currency_id)

        if success:
            self.send_redirect('/currencies')
        else:
            self.send_error(404, "Currency not found or could not be deleted")

    def handle_delete_user(self, user_id):
        """Удаление пользователя"""
        success = user_controller.delete_user(user_id)

        if success:
            self.send_redirect('/users')
        else:
            self.send_error(404, "User not found or could not be deleted")

    def handle_create_currency(self, form_data):
        """Создание валюты"""
        try:
            num_code = form_data.get('num_code', [''])[0]
            char_code = form_data.get('char_code', [''])[0]
            name = form_data.get('name', [''])[0]
            value = float(form_data.get('value', ['0'])[0])
            nominal = int(form_data.get('nominal', ['1'])[0])

            currency_controller.create_currency(num_code, char_code, name, value, nominal)
            self.send_redirect('/currencies')
        except (ValueError, KeyError) as e:
            self.send_error(400, f"Invalid currency data: {str(e)}")

    def handle_update_currency(self, form_data):
        """Обновление валют"""
        try:
            currency_id = int(form_data.get('id', [''])[0])

            update_data = {}
            if form_data.get('char_code', [''])[0]:
                update_data['char_code'] = form_data['char_code'][0]
            if form_data.get('name', [''])[0]:
                update_data['name'] = form_data['name'][0]
            if form_data.get('value', [''])[0]:
                update_data['value'] = float(form_data['value'][0])
            if form_data.get('nominal', [''])[0]:
                update_data['nominal'] = int(form_data['nominal'][0])

            success = currency_controller.update_currency(currency_id, **update_data)

            if success:
                self.send_redirect('/currencies')
            else:
                self.send_error(404, "Currency not found or could not be updated")
        except (ValueError, KeyError) as e:
            self.send_error(400, f"Invalid currency data: {str(e)}")

    def handle_create_user(self, form_data):
        """Создание пользователя"""
        try:
            name = form_data.get('name', [''])[0]
            user_controller.create_user(name)
            self.send_redirect('/users')
        except (ValueError, KeyError) as e:
            self.send_error(400, f"Invalid user data: {str(e)}")

    def handle_update_user(self, form_data):
        """Обновление пользователя"""
        try:
            user_id = int(form_data.get('id', [''])[0])
            name = form_data.get('name', [''])[0]

            if name:
                success = user_controller.update_user(user_id, name=name)
                if success:
                    self.send_redirect('/users')
                else:
                    self.send_error(404, "User not found or could not be updated")
            else:
                self.send_error(400, "Name is required")
        except (ValueError, KeyError) as e:
            self.send_error(400, f"Invalid user data: {str(e)}")

    def handle_update_currencies(self):
        """Обновление курсов валют"""
        success, message = update_currency_rates()

        currencies = currency_controller.list_currencies()

        template = env.get_template("currencies.html")
        result = template.render(
            currencies=currencies,
            update_message=message,
            update_success=success,
            navigation=[
                {'caption': 'Главная', 'href': '/'},
                {'caption': 'Пользователи', 'href': '/users'},
            ]
        )
        self.send_html_response(result)

if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 8081), SimpleHTTPRequestHandler)
    print('Server is running on http://localhost:8081')

    try:
        httpd.serve_forever()
    finally:
        db_controller.close()
