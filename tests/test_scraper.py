import unittest
import requests


class TestScraper(unittest.TestCase):
    def test_status_request(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        url = "https://github.com/backend-br/vagas/issues"
        site = requests.get(url, headers=headers, timeout=10)
        self.assertEqual(site.status_code, 200)


if __name__ == "__main__":
    unittest.main()
