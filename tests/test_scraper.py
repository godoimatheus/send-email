import unittest
from io import StringIO
from unittest.mock import patch, Mock, MagicMock
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from bs4 import BeautifulSoup
from src import scraper


class TestDatabaseConnection(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_connect_to_database(self, mock_stdout):
        result = scraper.connect_to_database()
        self.assertIsNotNone(result)
        self.assertIn(
            "Successfully connected to the database...", mock_stdout.getvalue()
        )

        self.assertIsInstance(result, Collection)
        indexes = result.index_information()
        self.assertTrue("issue_number_1" in indexes)

    @patch("src.scraper.MongoClient")
    def test_connection_error_database(self, mock_mongo_client):
        mock_instance = mock_mongo_client.return_value
        mock_instance.admin.command.side_effect = PyMongoError("Error")
        result = scraper.connect_to_database()
        self.assertIsNone(result)


class TestScraping(unittest.TestCase):
    def setUp(self) -> None:
        self.html = """
        <div class="flex-auto d-none d-lg-block no-wrap">
            <div class="table-list-header-toggle states flex-auto pl-0" aria-live="polite">
                <a href="/backend-br/vagas/issues?q=is%3Aissue+mail+in%3Abody+label%3APython+is%3Aopen" class="btn-link " data-ga-click="Issues, Table state, Open" data-turbo-frame="repo-content-turbo-frame">
                <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-issue-opened">
                <path d="M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path><path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z"></path>
            </svg>
                3 Open
                </a>
                <a href="/backend-br/vagas/issues?q=is%3Aissue+mail+in%3Abody+label%3APython+is%3Aclosed" class="btn-link " data-ga-click="Issues, Table state, Closed" data-turbo-frame="repo-content-turbo-frame">
                <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-check">
                <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path>
            </svg>
                402 Closed
                </a>
            </div>
        </div>
        """

    @patch("requests.get")
    @patch("bs4.BeautifulSoup")
    def test_scraping_site(self, mock_bs4, mock_requests):
        mock_requests.return_value.content = b"HTML content"
        mock_bs4.return_value = Mock()
        result = scraper.scraping_site("https://example.com")
        self.assertIsNotNone(result)

    def test_get_number_of_issues(self):
        soup = BeautifulSoup(self.html, "html.parser")
        result = scraper.get_number_of_issues(soup)
        self.assertEqual(result, 405)

    def test_get_number_of_pages_less_than_or_equal_to_25(self):
        html = ""
        soup = BeautifulSoup(html, "html.parser")
        self.assertFalse(soup.find("div", class_="pagination"))
        # last_page = soup.find("div", class_="pagination").text.strip().split(" ")[-2]
        last_page = scraper.get_number_of_pages(soup, 25)
        self.assertEqual(last_page, 1)

    def test_get_number_of_pages_greater_than_25(self):
        html = """
        <div role="navigation" aria-label="Pagination" class="pagination"><span class="previous_page disabled" aria-disabled="true">Previous</span> <em class="current" data-total-pages="17">1</em> <a rel="next" aria-label="Page 2" href="/backend-br/vagas/issues?page=2&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">2</a> <a aria-label="Page 3" href="/backend-br/vagas/issues?page=3&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">3</a> <a aria-label="Page 4" href="/backend-br/vagas/issues?page=4&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">4</a> <a aria-label="Page 5" href="/backend-br/vagas/issues?page=5&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">5</a> <span class="gap">…</span> <a aria-label="Page 16" href="/backend-br/vagas/issues?page=16&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">16</a> <a aria-label="Page 17" href="/backend-br/vagas/issues?page=17&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">17</a> <a class="next_page" rel="next" href="/backend-br/vagas/issues?page=2&amp;q=is%3Aissue+mail+in%3Abody+label%3APython">Next</a></div>
        """
        soup = BeautifulSoup(html, "html.parser")
        self.assertTrue(soup.find("div", class_="pagination"))
        total_issues = 425
        last_page = scraper.get_number_of_pages(soup, total_issues)
        self.assertEqual(int(last_page), 17)


class TestDatabaseInsertOrUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.database = scraper.connect_to_database()
        self.collection = MagicMock()
        self.issue_data_insert = {
            "_id": 1,
            "issue_number": "#123456",
            "status": "Closed as not planned issue",
            "title": "Title of issue",
            "last_update": "2023-01-01T00:49:33.000+00:00",
            "labels": ["Python", "Django", "Flask"],
            "author": "NameOfAuthor",
            "author_page": "https://github.com/NameOfAuthor",
            "url_issue": "https://github.com/backend-br/vagas/issues/123456",
            "email": "nameofauthor@email.com",
            "search_time": "2023-08-01T00:49:33.000+00:00",
            "send": False,
        }
        self.issue_data_update = {
            "_id": 1,
            "issue_number": "#123456",
            "status": "Open",
            "title": "Title of issue",
            "last_update": "2023-01-01T00:49:33.000+00:00",
            "labels": ["Python", "Django", "Flask"],
            "author": "NameOfAuthor",
            "author_page": "https://github.com/NameOfAuthor",
            "url_issue": "https://github.com/backend-br/vagas/issues/123456",
            "email": "nameofauthor@email.com",
            "search_time": "2023-08-01T00:49:33.000+00:00",
            "send": False,
        }

    @patch("sys.stdout", new_callable=StringIO)
    def test_insert_one_to_database(self, mock_stdout):
        scraper.insert_or_update_database(self.collection, self.issue_data_insert)
        self.collection.insert_one.assert_called_with(self.issue_data_insert)
        self.assertIn(
            f"{self.issue_data_insert['issue_number']}: Successfully added",
            mock_stdout.getvalue(),
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_one_in_database(self, mock_stdout):
        self.collection.insert_one.side_effect = DuplicateKeyError("test error")
        scraper.insert_or_update_database(self.collection, self.issue_data_insert)
        self.assertIn(
            f"{self.issue_data_update['issue_number']}: Successfully update",
            mock_stdout.getvalue(),
        )
