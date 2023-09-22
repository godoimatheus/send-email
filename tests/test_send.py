import unittest
from unittest.mock import patch
from io import StringIO
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from src import send


class TestDatabaseConnection(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_connect_to_database(self, mock_stdout):
        result = send.connect_to_database()
        self.assertIsNotNone(result)
        self.assertIn(
            "Successfully connected to the database...", mock_stdout.getvalue()
        )

        self.assertIsInstance(result, Collection)
        indexes = result.index_information()
        self.assertTrue("issue_number_1" in indexes)

    @patch("src.send.MongoClient")
    def test_connection_error_database(self, mock_mongo_client):
        mock_instance = mock_mongo_client.return_value
        mock_instance.admin.command.side_effect = PyMongoError("Error")
        result = send.connect_to_database()
        self.assertIsNone(result)
