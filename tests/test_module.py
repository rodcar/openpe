
import unittest
from openpe import example_function, Categories

class TestModule(unittest.TestCase):
    def test_example_function(self):
        self.assertEqual(example_function(), "Hello, World!")

    def test_add_new_category(self):
        Categories.register_category("NEW_EDUCACION", "Educación")
        self.assertEqual(Categories.NEW_EDUCACION, "Educación")

if __name__ == '__main__':
    unittest.main()