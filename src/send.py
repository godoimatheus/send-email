import smtplib
import email.message
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from user import MY_EMAIL, MY_PASSWORD

uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(uri, server_api=ServerApi("1"))
try:
    client.admin.command("ping")
    print("Conectando ao banco de dados")
except Exception as e:
    print(e)
db = client["issues"]
collection = db["vagas"]


def send_email():
    email_list = collection.distinct("email")
    for email_issues in email_list:
        body_email = "áéíóú"
        msg = email.message.Message()
        msg["Subject"] = "Assunto"
        msg["From"] = MY_EMAIL
        msg["To"] = email_issues
        password = MY_PASSWORD
        msg.add_header("Content-Type", "text/html; charset=utf-8")
        msg.set_payload(body_email, "utf-8")
        smtp = smtplib.SMTP("smtp.gmail.com: 587")
        smtp.starttls()
        smtp.login(msg["From"], password)
        smtp.sendmail([msg["From"]], [msg["To"]], msg.as_string().encode("utf-8"))
        print(f"Sending email to: {email_issues}")
    print("Finished sending the emails")


# send_email()
