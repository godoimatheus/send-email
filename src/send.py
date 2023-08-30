import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# from email.mime.application import MIMEApplication
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from settings import MY_EMAIL, MY_PASSWORD
from settings import MY_SUBJECT, MY_BODY

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
    email_list = collection.distinct("email", {"send": False})
    for email in email_list[:50]:
        if email == "not found":
            continue

        msg = MIMEMultipart()
        msg["From"] = MY_EMAIL
        password = MY_PASSWORD
        msg["To"] = email
        msg["Subject"] = MY_SUBJECT
        body = MY_BODY
        msg.attach(MIMEText(body, "html"))

        # pdf_path = "cv/curriculum.pdf"
        # with open(pdf_path, "rb") as pdf:
        #     pdf_att = MIMEApplication(pdf.read(), _subtype="pdf")
        #     pdf_att.add_header(
        #         "content-disposition", "attachment; filename=curriculum.pdf"
        #     )
        #     msg.attach(pdf_att)

        smtp = smtplib.SMTP("smtp.gmail.com: 587")
        smtp.starttls()
        smtp.login(msg["From"], password)
        smtp.sendmail([msg["From"]], [msg["To"]], msg.as_string().encode("utf-8"))
        smtp.quit()
        print(f"Sending email to: {email}")

        collection.update_many({"email": email}, {"$set": {"send": True}})

    print("Finished sending the emails")


if __name__ == "__main__":
    send_email()
