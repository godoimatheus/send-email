import requests
from bs4 import BeautifulSoup


def extrair_vagas():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    url = "https://github.com/backend-br/vagas/issues?q=is%3Aissue+mail+in%3Abody+label%3APython+is%3Aopen"
    site = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(site.content, "html.parser")
    jobs = soup.find_all(
        "div",
        class_="Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row",
    )
    print(len(jobs))
    for job in jobs:
        title = job.find(
            class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title"
        ).get_text()
        print(title)
        # labels
        # issue_number
        # opened
        # author
        # status
        # email


extrair_vagas()
