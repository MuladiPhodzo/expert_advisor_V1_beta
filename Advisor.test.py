import unittest

from Advisor import add


class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(10, 20), 30)
        self.assertEqual(add(100, 200), 300)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -2), -3)
        self.assertEqual(add(-10, -20), -30)
        self.assertEqual(add(-100, -200), -300)

    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(0, 10), 10)
        self.assertEqual(add(10, 0), 10)

    def test_add_mixed_numbers(self):
        self.assertEqual(add(1, 2, 3), 6)
        self.assertEqual(add(10, 20, 30), 60)
        self.assertEqual(add(100, 200, 300), 600)


if __name__ == '__main__':
    unittest.main()