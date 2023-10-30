import smtplib
from email.message import EmailMessage
import ssl
import os
import time


# 587
# import openpyxl
def sendEmailsScript(email, sendee, app_password, body, subject):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    em = EmailMessage()
    em["From"] = email
    em["subject"] = subject
    em["To"] = sendee
    em.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        # login with email and the app password they created
        smtp.login(email, app_password)
        time.sleep(3)

        try:
            smtp.sendmail(email, sendee, em.as_string())
        except:
            return "Not Successful Send"

    return "Sent all possible emails"
