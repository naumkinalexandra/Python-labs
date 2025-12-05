import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, PackageLoader, select_autoescape
from import Author, App, User, Currency, UserCurrency
from utils.currencies_api import get_currencies

main_author = Author(name="sasha naumkina", group="P-3122")
main_app = App(name="Currency Tracker", version="1.0", author=main_author)


USERS = {
    1: User(1, "Sasha"),
    2: User(2, "Nick"),
    3: User(3, "Alex"),
}

CURRENCIES: dict[str, Currency] = {}
SUBSCRIPTIONS: list[UserCurrency] = []


def setup_initial_data():
    """Заполняет CURRENCIES и SUBSCRIPTIONS при старте."""
    global CURRENCIES, SUBSCRIPTIONS

    CURRENCIES = get_currencies()

    if CURRENCIES:
        usd = CURRENCIES.get('USD')
        eur = CURRENCIES.get('EUR')

        if usd:
            SUBSCRIPTIONS.append(UserCurrency(USERS[1], usd, 1))
        if eur:
            SUBSCRIPTIONS.append(UserCurrency(USERS[1], eur, 2))

        jpy = CURRENCIES.get('JPY')
        if jpy:
            SUBSCRIPTIONS.append(UserCurrency(USERS[2], jpy, 3))

    print(f"Сервер запущен. Загружено {len(CURRENCIES)} валют и {len(SUBSCRIPTIONS)} подписок.")


env = Environment(
    loader=PackageLoader("myapp", "templates"),
    autoescape=select_autoescape(['html', 'xml'])
)


try:
    template_index = env.get_template("index.html")
    template_users = env.get_template("users.html")
    template_user_detail = env.get_template("user_detail.html")
    template_currencies = env.get_template("currencies.html")
    template_author = env.get_template("author.html")
except Exception as e:
    print(f"Ошибка загрузки шаблонов: {e}")
    exit(1)


def get_navigation(current_path: str):
    """Возвращает список для навигационной панели."""
    nav_items = [
        {'caption': 'Главная', 'href': '/'},
        {'caption': 'Пользователи', 'href': '/users'},
        {'caption': 'Курсы валют', 'href': '/currencies'},
        {'caption': 'Автор', 'href': '/author'},
    ]
    for item in nav_items:
        if item['href'] == current_path:
            item['active'] = True
        else:
            item['active'] = False
    return nav_items



class SimpleHTTPController(BaseHTTPRequestHandler):
    """
    Контроллер, обрабатывающий HTTP-запросы и маршрутизирующий их.
    """

    def do_GET(self):
        """Обрабатывает GET-запросы."""

        # Парсим URL: self.path содержит полный путь, включая query-параметры
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        navigation = get_navigation(path)

        if path == '/':
            self.handle_index(navigation)
        elif path == '/users':
            self.handle_users(navigation)
        elif path == '/user':
            self.handle_user_detail(navigation, query_params)
        elif path == '/currencies':
            self.handle_currencies(navigation)
        elif path == '/author':
            self.handle_author(navigation)
        elif path.startswith('/static/'):
            self.handle_static_file(path)
        else:
            self.handle_404(path, navigation)


    def _render_and_send(self, template, context: dict, status=200):
        """Рендерит шаблон и отправляет ответ клиенту."""

        context['app'] = main_app

        try:
            html_content = template.render(**context)
            self.send_response(status)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except Exception as e:
            print(f"Ошибка при рендеринге: {e}")
            self.handle_500(str(e))
   def handle_index(self, navigation: list):
        """Главная страница: /"""
        context = {
            'page_title': 'Главная',
            'navigation': navigation,
            'app_name': main_app.name,
            'app_version': main_app.version,
            'author_name': main_author.name,
            'group': main_author.group,
        }
        self._render_and_send(template_index, context)

    def handle_users(self, navigation: list):
        """Страница со списком пользователей: /users"""
        context = {
            'page_title': 'Пользователи',
            'navigation': navigation,
            'users_list': list(USERS.values()),
        }
        self._render_and_send(template_users, context)

    def handle_user_detail(self, navigation: list, query_params: dict):
        """Страница с деталями пользователя: /user?id=..."""

        user_id_list = query_params.get('id')
        if not user_id_list:
            self.handle_404("Отсутствует параметр id для пользователя", navigation)
            return

        try:
            user_id = int(user_id_list[0])
        except ValueError:
            self.handle_404("Некорректный ID пользователя", navigation)
            return

        user = USERS.get(user_id)
        if not user:
            self.handle_404(f"Пользователь с ID={user_id} не найден", navigation)
            return

        user_subscriptions = [
            sub.currency
            for sub in SUBSCRIPTIONS
            if sub.user.id == user.id
        ]

        context = {
            'page_title': f"Пользователь: {user.name}",
            'navigation': navigation,
            'current_user': user,
            'subscriptions': user_subscriptions,
        }
        self._render_and_send(template_user_detail, context)

    def handle_currencies(self, navigation: list):
        """Страница со списком валют: /currencies"""

        global CURRENCIES
        CURRENCIES = get_currencies()
        context = {
            'page_title': 'Курсы валют',
            'navigation': navigation,
            'currencies_list': sorted(
                list(CURRENCIES.values()),
                key=lambda c: c.char_code
            ),
        }
        self._render_and_send(template_currencies, context)

    def handle_author(self, navigation: list):
        """Страница с информацией об авторе: /author"""
        context = {
            'page_title': 'Информация об авторе',
            'navigation': navigation,
            'author': main_author,
            'app': main_app
        }
        self._render_and_send(template_author, context)


    def handle_static_file(self, path: str):
        """Обработка статических файлов из папки /static/"""
        file_path = path[1:]
        if not file_path.startswith('static/'):
            self.handle_404(f"Запрещенный доступ: {path}", [])
            return

        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            if file_path.endswith('.css'):
                mime_type = 'text/css'
            elif file_path.endswith('.js'):
                mime_type = 'application/javascript'
            elif file_path.endswith('.png'):
                mime_type = 'image/png'
            else:
                mime_type = 'application/octet-stream'  # Для неизвестных типов

            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.handle_404(f"Статический файл не найден: {path}", [])
        except Exception as e:
            print(f"Ошибка при обработке статического файла: {e}")
            self.handle_500(f"Ошибка чтения файла: {path}")

    def handle_404(self, message: str, navigation: list):
        """Обработчик 404 Not Found."""
        self.send_response(404)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html_content = f"""
        <html>
            <head><title>404 Not Found</title></head>
            <body>
                <h1>404 Not Found</h1>
                <p>Страница не найдена: <b>{self.path}</b></p>
                <p>{message}</p>
                <p><a href="/">На главную</a></p>
            </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    def handle_500(self, message: str):
        """Обработчик 500 Internal Server Error."""
        self.send_response(500)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        html_content = f"""
        <html>
            <head><title>500 Internal Server Error</title></head>
            <body>
                <h1>500 Internal Server Error</h1>
                <p>Произошла внутренняя ошибка сервера.</p>
                <p>Детали: {message}</p>
            </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleHTTPController, port=8000):
    """Запускает HTTP-сервер."""

    setup_initial_data()

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f"Сервер запущен на http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()


if __name__ == '__main__':
    run()