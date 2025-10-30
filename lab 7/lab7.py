import unittest
import io


# Тесты
class TestStreamWrite(unittest.TestCase):


  def setUp(self):
    self.nonstandardstream = io.StringIO()
    self.trace = trace(get_currencies, handle=self.nonstandardstream)


  def test_writing_stream(self):
    with self.assertRaises(requests.exceptions.RequestException):
      self.trace(['USD'], url="https://")


  def tearDown(self):
    del self.nonstandardstream




# Запуск тестов
unittest.main(argv=[''], verbosity=2, exit=False)