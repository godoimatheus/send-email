import re
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError


def connect_to_database():
    try:
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        client = MongoClient(uri, server_api=ServerApi("1"))
        client.admin.command("ping")
        print("Successfully connected to the database..")
        database = client["issues"]
        database_collection = database["vagas"]
        database_collection.create_index(
            [("issue_number", pymongo.ASCENDING)], unique=True
        )
        print("Created index")
        return database_collection
    except PyMongoError as erro:
        print("Error:", erro)
        return None


collection = connect_to_database()


def scraping_site(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    site = requests.get(url, headers=headers, timeout=10)
    html_soup = BeautifulSoup(site.content, "html.parser")
    return html_soup


soup = scraping_site(
    "https://github.com/backend-br/vagas/issues?q=is%3Aissue+email+OR+mail+in%3Abody+label%3APython"
)


def number_of_issues():
    open_issues = (
        soup.find("div", class_="flex-auto d-none d-lg-block no-wrap")
        .text.strip()
        .split(" ")[0]
    )
    print(f"Open issues: {open_issues}")
    closed_issues = (
        soup.find("div", class_="flex-auto d-none d-lg-block no-wrap")
        .text.strip()
        .split(" ")[-2]
    )
    print(f"Closed issues: {closed_issues}")
    total_issues = int(open_issues) + int(closed_issues)
    print(f"total issues: {total_issues}")
    return total_issues


issues = number_of_issues()


def number_of_pages():
    if issues > 25:
        last_page = soup.find("div", class_="pagination").text.strip().split(" ")[-2]
        print(f"Total pages: {last_page}")
        return last_page
    return "1"


total_pages = number_of_pages()

for page in range(1, int(total_pages) + 1):
    print(f"Page: {page}")
    soup = scraping_site(
        f"https://github.com/backend-br/vagas/issues?page={page}&q=is%3Aissue+email+OR+mail+in%3Abody+label%3APython"
    )
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
        issue_date = datetime.strptime(opened, "%Y-%m-%dT%H:%M:%SZ")
        print(issue_date)

        labels = job.find_all("a", class_="IssueLabel hx_IssueLabel")
        labels_list = []
        for label in labels:
            labels_list.append(label.get_text().strip())
        print(labels_list)

        author = job.find("a", class_="Link--muted").get_text()
        print(author)

        URL_GITHUB = "https://github.com"

        url_author = URL_GITHUB + "/" + author
        print(url_author)

        link_job = job.find(
            "a",
            class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title",
        ).get("href")
        url_job = URL_GITHUB + link_job
        print(url_job)
        soup = scraping_site(url_job)
        job_detail = soup.find("div", class_="edit-comment-hide")
        try:
            EMAIL = job_detail.find(href=re.compile("mailto")).get_text()
            print(EMAIL)
        except AttributeError:
            EMAIL = "not found"
            print(EMAIL)
        search_time = datetime.utcnow()
        try:
            collection.insert_one(
                {
                    "issue_number": issue_number,
                    "status": status,
                    "title": title,
                    "last_update": issue_date,
                    "labels": labels_list,
                    "author": author,
                    "author_page": url_author,
                    "email": EMAIL,
                    "url_issue": url_job,
                    "search_time": search_time,
                }
            )
        except DuplicateKeyError:
            collection.update_one(
                {"issue_number": issue_number},
                {
                    "$set": {
                        "status": status,
                        "title": title,
                        "last_update": issue_date,
                        "labels": labels_list,
                        "author": author,
                        "author_page": url_author,
                        "email": EMAIL,
                        "url_issue": url_job,
                        "search_time": search_time,
                    }
                },
            )
        print()
