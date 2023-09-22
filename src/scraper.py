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
        print("Successfully connected to the database...")
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


def scraping_site(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    site = requests.get(url, headers=headers, timeout=10)
    html_soup = BeautifulSoup(site.content, "html.parser")
    return html_soup


def get_number_of_issues(soup_num_issues):
    open_issues = (
        soup_num_issues.find("div", class_="flex-auto d-none d-lg-block no-wrap")
        .text.strip()
        .split(" ")[0]
    )
    closed_issues = (
        soup_num_issues.find("div", class_="flex-auto d-none d-lg-block no-wrap")
        .text.strip()
        .split(" ")[-2]
    )
    total_issues = int(open_issues) + int(closed_issues)
    return total_issues


def get_number_of_pages(soup, total_issues):
    if total_issues > 25:
        last_page = soup.find("div", class_="pagination").text.strip().split(" ")[-2]
        print(f"Total pages: {last_page}")
        return last_page
    return 1


def insert_or_update_database(collection_db, issue_data_db):
    try:
        collection_db.insert_one(issue_data_db)
        print(f"{issue_data_db['issue_number']}: Successfully added")
    except DuplicateKeyError:
        issue_data_db.pop("_id")
        collection_db.update_one(
            {"issue_number": issue_data_db["issue_number"]},
            {"$set": issue_data_db},
        )
        print(f"{issue_data_db['issue_number']}: Successfully update")


if __name__ == "__main__":
    collection = connect_to_database()
    URL_GITHUB = "https://github.com"
    BASE_URL = (
        URL_GITHUB
        + "/backend-br/vagas/issues?q=is%3Aissue+email+OR+mail+in%3Abody+label%3APython"
    )
    soup_base = scraping_site(BASE_URL)
    get_number_of_issues(soup_base)
    final_page = get_number_of_pages(soup_base, get_number_of_issues(soup_base))

    for page in range(1, int(final_page) + 1):
        print(f"Page: {page}")
        page_url = (
            URL_GITHUB
            + f"/backend-br/vagas/issues?page={page}&q=is%3Aissue+email+OR+mail+in%3Abody+label%3APython"
        )
        soup_issues = scraping_site(page_url)
        jobs = soup_issues.find_all(
            "div",
            class_="Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row",
        )

        for job in jobs:
            issue_data = {}
            issue_data["issue_number"] = (
                job.find("span", class_="opened-by").get_text().strip().split("\n")[0]
            )

            issue_data["status"] = job.find(
                "span", class_="tooltipped tooltipped-e"
            ).get("aria-label")

            issue_data["title"] = job.find(
                class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title"
            ).get_text()

            opened = job.find("relative-time").get("datetime")
            issue_data["last_update"] = datetime.strptime(opened, "%Y-%m-%dT%H:%M:%SZ")

            labels = job.find_all("a", class_="IssueLabel hx_IssueLabel")
            labels_list = []
            for label in labels:
                labels_list.append(label.get_text().strip())
            issue_data["labels"] = labels_list

            author = job.find("a", class_="Link--muted").get_text()
            issue_data["author"] = author

            issue_data["author_page"] = URL_GITHUB + "/" + author

            link_job = job.find(
                "a",
                class_="Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title",
            ).get("href")

            # find email
            url_job = URL_GITHUB + link_job
            issue_data["url_issue"] = url_job
            soup_email = scraping_site(url_job)
            job_detail = soup_email.find("div", class_="edit-comment-hide")
            try:
                EMAIL = job_detail.find(href=re.compile("mailto")).get_text()
                issue_data["email"] = EMAIL
            except AttributeError:
                EMAIL = "not found"
                issue_data["email"] = EMAIL

            issue_data["search_time"] = datetime.utcnow()

            issue_data["send"] = False

            if issue_data["email"] in collection.distinct("email"):
                send_status = collection.find_one({"email": issue_data["email"]})
                issue_data["send"] = send_status["send"]

            insert_or_update_database(collection, issue_data)
