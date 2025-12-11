# models.py
class App:
    def __init__(self, name, version):
        self.name = name
        self.version = version

class User:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

class Currency:
    def __init__(self, currency_id, num_code, char_code, name, value, nominal):
        self.id = currency_id
        self.num_code = num_code
        self.char_code = char_code
        self.name = name
        self.value = value
        self.nominal = nominal

class UserCurrency:
    def __init__(self, user_currency_id, user_id, currency_id):
        self.id = user_currency_id
        self.user_id = user_id
        self.currency_id = currency_id