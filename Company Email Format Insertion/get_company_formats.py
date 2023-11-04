# asyncio import
import asyncio

# Beautiful Soup 4
from bs4 import BeautifulSoup

# Webscraping imports
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
import undetected_chromedriver as uc

# working with environment variable imports
import os
from dotenv import load_dotenv

# insertCompanyEmailFormat function
import insert_format_todb

# firebase imports
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

# for undetected chromedriver
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize the Firebase Admin SDK with your service account credentials
current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(
    "/Users/mac/Desktop/Projects/Automated-Email-Script/",
    "serviceAccountKey.json",
)

cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://ans-application-f2bdc-default-rtdb.firebaseio.com"}
)


# Path to chromebrowser and driver
PATH_TO_CHROMEDRIVER = (
    "/Users/mac/Desktop/Projects/Chrome Driver/chromedriver-mac-x64/chromedriver"
)
PATH_TO_CHROMEBROWSER = "/Users/mac/Desktop/Projects/Chrome Driver/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
# ------------------------------------------------------------------------------------------------------------------------------ #


async def getCompanyEmailFormats(companies: list, companies_ref):
   # CHROME DRIVER OPTIONS
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.binary_location = PATH_TO_CHROMEBROWSER
    # ------------------------------------------------------------------------------------------------------------------------------ #

    # Driver - Browser
    driver = webdriver.Chrome(
        service=Service(executable_path=PATH_TO_CHROMEDRIVER), options=chrome_options
    )

    # go to rocket reach
    driver.get("https://rocketreach.co/login?next=%2F")

    # log in manually
    process = input("Did you finish logging in? ")

    while process.lower().strip() != "yes":
        process = input("Did you finish logging in? ")

    # get companies page
    driver.get("https://rocketreach.co/company?start=1&pageSize=10")

    for i in range(len(companies)):
        email_formats = []

        # locate the search bar and enter the current company
        while True:
            try:
                search = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/div/rr-keyword-search-facet-input/form/div/div/input",
                )

                # enter the company in the search bar
                search.clear()
                search.send_keys(companies[i])
                search.send_keys(Keys.RETURN)
                break
            except:
                driver.refresh()
                sleep(3)
                continue    

        # wait until the table of search results appears
        while True:
            try:
                # wait for ul tag containing search results
                WebDriverWait(driver, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/rr-unified-search-results/div/div[3]/div/ul"))
                )
                # click on the first element of the search results table to get to the emails
                results_list = driver.find_element(By.CLASS_NAME, "search-results-list")
                rows = results_list.find_elements(By.TAG_NAME, "li")
                first_element = rows[0]

                # get the first element and click on it
                first_element = rows[0].find_element(By.CLASS_NAME, "profile-image-wpr")
                first_element.click()
                break
            except:
                sleep(1)
                continue

        # switch to new tab
        driver.switch_to.window(driver.window_handles[1])

        # Locate the email format tab
        while True:
            try:
                WebDriverWait(driver, timeout=10).until(
                    EC.visibility_of_element_located(
                        (
                            By.CLASS_NAME,
                            "nav nav-tabs row no-gutters",
                        )
                    )
                )

                # click on email format tab
                driver.find_element(
                    By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div/ul/li[2]/a"
                ).click()
                

                # Wait for the table to appear
                WebDriverWait(driver, timeout=10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div/div[3]/div[1]/div/div/div/div[1]/div[2]/div/table",
                        )
                            
                    )
                )
                break
            except:
                driver.refresh()
                sleep(3)
                continue

        # get the source for bs4 to work
        curr_page = driver.page_source
        doc = BeautifulSoup(curr_page, "html.parser")

        # need to establish connection point
        major = doc.find("table", class_="table")
        while major is None:
            major = doc.find("table", class_="table")
            sleep(1)
        
        # find all the table rows
        trs = major.tbody.find_all("tr")

        email_format = ""
        example = ""
        accuracy = ""

        for tr in trs:
            tds = tr.find_all("td")

            # collect all structured ordered data
            email_format = tds[0].get_text()
            example = tds[1].get_text()
            accuracy = tds[-1].div.span.get_text()

            # put the info into the list of email formats
            email_formats = [email_format, example, accuracy]

        # insert into firebase db
        new_id = await insert_format_todb.insertCompanyEmailFormat(
            email_formats, companies_ref
        )
        print("New inputted company: ", new_id)

        # close tab and get to new company
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        print(email_formats)

    # end of program
    driver.quit()
    return email_formats


if __name__ == "__main__":
    companies = ["Datadog"]
    # Access the Firestore database
    db = firestore.client()
    companies_ref = db.collection("Companies")

    asyncio.run(getCompanyEmailFormats(companies, companies_ref))
