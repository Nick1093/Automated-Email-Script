from bs4 import BeautifulSoup
import requests

import pandas as pd

# firebase
import firebase_admin
from firebase_admin import credentials, firestore

# generate email function 
import generate_email 

# import requests
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

from dotenv import load_dotenv

# import csv
# import re
import os
from selenium.webdriver.chrome.options import Options


import undetected_chromedriver as uc

# import ssl

# ssl._create_default_https_context = ssl._create_unverified_context

# Path to chromedriver
PATH_TO_CHROMEDRIVER = "/Users/mac/Desktop/Projects/Email Script/chromedriver-mac-x64/chromedriver"

# Path to chromebrowser
PATH_TO_CHROMEBROWSER = "/Users/mac/Desktop/Projects/Email Script/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"


# Initialize the Firebase Admin SDK with your service account credentials
current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_dir, "serviceAccountKey.json")

cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://ans-application-f2bdc-default-rtdb.firebaseio.com"}
)

# Access the Firestore database
db = firestore.client()

# Load environment variables from .env file
load_dotenv()

# for dataframe
column_names = ["Name", "Company", "Location", "Email"]
file_name = "Email_Formats.xlsx"
df = pd.DataFrame(columns=column_names)

# starting row for data frame
df_row = 1


def scrapingAlgorithm(link, companies_ref):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("start-maximized")
    chrome_options.binary_location = PATH_TO_CHROMEBROWSER

    driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER, options=chrome_options)

    username = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("LINKEDIN_PASS")

    driver.get(link)

    # wait for page to load
    WebDriverWait(driver, timeout=10).until(
        EC.element_to_be_clickable(
            (
                By.CLASS_NAME,
                "main__sign-in-link",
            )
        )
    )

    driver.find_element(By.CLASS_NAME, "main__sign-in-link").click()

    user = driver.find_element(By.ID, "username")
    user.send_keys(username)
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)


    # wait for table to load
    WebDriverWait(driver, timeout=10).until(
        EC.visibility_of_all_elements_located(
            (
                By.CLASS_NAME,
                "reusable-search__result-container",
            )
        )
    )

    # get pages
    try:
        pages = driver.find_element(
            By.CLASS_NAME,
            "artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view",
        )
        print("found pages ", pages)
    except:
        print("not found pages")
        pages = 100

    # loop through each page to scrape information
    for i in range(1, pages):
        # information to scrape
        name = None
        emails = None
        company = None
        location = None

        # update current page
        link = f"{link}&page={i}"

        try:
            # get current page
            driver.get(link)
        except:
            driver.quit()
            break

        # get the source for bs4 to work
        curr_page = driver.page_source
        doc = BeautifulSoup(curr_page, "html.parser")

        # major = doc.find(["div"], class_="ph0 pv2 artdeco-card mb2").ul
        major = doc.find("div", class_="pv0 ph0 mb2 artdeco-card")
        people_list = major.find(
            "ul", class_="reusable-search__entity-result-list list-style-none"
        )

        people = people_list.find_all("li", class_="reusable-search__result-container")

        # loop through each person on the page
        for p in people:
            # get the Linkedin Member's Name
            try:
                name = p.find(
                    "div",
                    class_="ivm-view-attr__img-wrapper ivm-view-attr__img-wrapper--use-img-tag display-flex",
                )
                name = name.find("img", alt=True)["alt"].lower()
            except:
                print("Name failed")
                name = None

            # alternative way if first one doesnt work
            if name == None or name == "":
                try:
                    name = p.find(
                        "span",
                        class_="entity-result__title-text t-16",
                    )
                    name = (
                        name.find("a")
                        .get_text()
                        .replace("\n", "")
                        .replace("'s", "")
                        .replace(" profile", "")
                        .lower()
                    )
                    if name == "linkedin member":
                        continue
                except:
                    print("Name failed 2")
                    continue

            # get individuals company
            try:
                company = (
                    p.find(
                        "div",
                        class_="entity-result__primary-subtitle t-14 t-black t-normal",
                    )
                    .get_text()
                    .replace("\n", "")
                    .replace("@", "")
                    .lower()
                )
            except:
                print("Company Failed")
                company = None

            # get Linkedin Member's location
            try:
                location = (
                    p.find(
                        "div", class_="entity-result__secondary-subtitle t-14 t-normal"
                    )
                    .get_text()
                    .replace("\n", "")
                    .lower()
                )
            except:
                print("location failed")
                location = ""

            if name and company:
                emails = generate_email(name, company, companies_ref)
                if emails == "Company not recognized in database":
                    continue
            else:
                emails = False

            # if potential emails found/created, add it to csv file
            if emails:
                df.loc[df_row] = [name, company, location, emails]
                df_row += 1

    df.to_excel("Data.xlsx", index=False)


df = pd.DataFrame(columns=column_names)



# scrapingAlgorithm(
#     "https://www.linkedin.com/search/results/people/?currentCompany=%5B%221337%22%2C%2220226%22%2C%221035%22%2C%221441%22%5D&geoUrn=%5B%22101174742%22%2C%22105149290%22%2C%22103644278%22%2C%2290009551%22%2C%22100025096%22%5D&industry=%5B%221594%22%2C%226%22%2C%224%22%2C%221810%22%2C%2243%22%5D&origin=FACETED_SEARCH&pastCompany=%5B%221337%22%2C%2220226%22%2C%221035%22%2C%221441%22%5D&schoolFilter=%5B%223660%22%2C%22166689%22%2C%22166688%22%2C%22220671%22%2C%22167012%22%5D&sid=ufy"
# )

# scrapingAlgorithm(
#     "https://www.linkedin.com/search/results/people/?currentCompany=%5B%221035%22%5D&origin=FACETED_SEARCH&schoolFilter=%5B%22166689%22%2C%22220671%22%5D&sid=8rq"
# )
