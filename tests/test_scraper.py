import unittest
from io import StringIO
from unittest.mock import patch
from src.scraper import connect_to_database


class TestDatabase(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_connect_to_database(self, mock_stdout):
        self.assertIsNotNone(connect_to_database())
        self.assertIn(
            "Successfully connected to the database...", mock_stdout.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
