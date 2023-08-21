import re
import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

URL = "https://github.com/backend-br/vagas/issues?q=is%3Aissue+mail+in%3Abody+label%3APython"
site = requests.get(URL, headers=headers, timeout=10)
soup = BeautifulSoup(site.content, "html.parser")
issues_open = (
    soup.find("div", class_="flex-auto d-none d-lg-block no-wrap")
    .text.strip()
    .split(" ")[0]
)
issues_closed = (
    soup.find("div", class_="flex-auto d-none d-lg-block no-wrap")
    .text.strip()
    .split(" ")[-2]
)
issues_total = int(issues_open) + int(issues_closed)
print(issues_total)
if issues_total > 25:
    last_page = soup.find("div", class_="pagination").text.strip().split(" ")[-2]
    print(last_page)

for page in range(1, int(last_page) + 1):
    print(f"Page: {page}")
    URL = f"https://github.com/backend-br/vagas/issues?page={page}&q=is%3Aissue+mail+in%3Abody+label%3APython"
    site = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(site.content, "html.parser")
    jobs = soup.find_all(
        "div",
        class_="Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row",
    )
    print(len(jobs))
    for job in jobs:
        issue_number = (
            job.find("span", class_="opened-by").get_text().strip().split("\n")[0]
        )
        print(issue_number)

        status = job.find("span", class_="tooltipped tooltipped-e").get("aria-label")
        print(status)

        title = job.find(
            class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title"
        ).get_text()
        print(title)

        opened = job.find("relative-time").get("datetime")
        print(opened)

        labels = job.find_all("a", class_="IssueLabel hx_IssueLabel")
        labels_list = []
        for label in labels:
            labels_list.append(label.get_text().strip())
        print(labels_list)

        author = job.find("a", class_="Link--muted").get_text()
        print(author)

        URL_GITHUB = "https://github.com"

        author_link = job.find("a", class_="Link--muted").get("href")
        url_author = URL_GITHUB + author_link
        print(url_author)

        link_job = job.find(
            "a",
            class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title",
        ).get("href")
        url_job = URL_GITHUB + link_job
        print(url_job)
        site = requests.get(url_job, headers=headers, timeout=10)
        soup = BeautifulSoup(site.content, "html.parser")
        job_detail = soup.find("div", class_="edit-comment-hide")
        try:
            EMAIL = job_detail.find(href=re.compile("mailto")).get_text()
            print(EMAIL)
        except AttributeError:
            EMAIL = "not found"
            print(EMAIL)
        print()
