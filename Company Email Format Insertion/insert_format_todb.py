# Web scraping Library Imports
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from selenium.webdriver.chrome.options import Options

# ------------------------------------------------------------------------------------------------------------------------------ #


#
import asyncio

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------------------------------------------------------------------------------------------------------------ #

# Pandas and openpyxl
import pandas as pd

# ------------------------------------------------------------------------------------------------------------------------------ #


# Load the excel file
# excel_file = "/Users/mac/Desktop/Projects/Email Script/Excel Data/Company_Details.xlsx"
# df = pd.read_excel(excel_file)
# ------------------------------------------------------------------------------------------------------------------------------ #


# Webscraping Algorithm
async def insertCompanyEmailFormat(companies, companies_ref):
    # set up variables - things to add
    email_formats = []

    for i in range(len(companies)):
        email_format = "{{0[first]}}{2[separator]}{{1[last]}}@{3[company]}"

        # string play with the format
        format = companies[0].replace("[", " ").replace("]", " ")
        current_format = format.split(" ")
        first = current_format[0]
        second = current_format[-1]

        if len(current_format) == 3:
            delimeter = current_format[1]
        else:
            delimeter = False

        company = companies[1].split("@")[1]

        accuracy = float(companies[-1].replace("%", ""))

        current_entry = email_format.format(
            {"first": first},
            {"last": second},
            {"separator": delimeter},
            {"company": company},
        )

        email_formats.append({"email_format": current_entry, "accuracy": accuracy})

    doc_id = companies_ref.add({"name": company, "email_formats": email_formats})

    return doc_id
