# asyncio import
import asyncio

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
    "/Users/mac/Desktop/Projects/Email Script/",
    "serviceAccountKey.json",
)

cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://ans-application-f2bdc-default-rtdb.firebaseio.com"}
)

# Access the Firestore database
db = firestore.client()
companies_ref = db.collection("Companies")


# Path to chromebrowser and driver
PATH_TO_CHROMEDRIVER = (
    "/Users/mac/Desktop/Projects/Chrome Driver/chromedriver-mac-x64/chromedriver"
)
PATH_TO_CHROMEBROWSER = "/Users/mac/Desktop/Projects/Chrome Driver/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
# ------------------------------------------------------------------------------------------------------------------------------ #


async def getCompanyEmailFormats(companies: list):
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
                break
            except:
                driver.refresh()
                sleep(1)
                continue    

        # enter the company in the search bar
        search.clear()
        search.send_keys(companies[i])
        search.send_keys(Keys.RETURN)

        # wait until the table of search results appears
        while True:
            try:
                WebDriverWait(driver, timeout=10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "search-results-list"))
                )
                break
            except:
                pass
        
            try:
                WebDriverWait(driver, timeout=10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/rr-unified-search-results/div/div[3]/div/ul",
                        )
                    )
                )
                break
            except:
                driver.refresh()
                sleep(1)
                continue

        # wait for the first element of the search results list to appear
        while True:
            try:
                WebDriverWait(driver, timeout=10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/rr-unified-search-results/div/div[3]/div/ul/li[1]/rr-company-search-result/div/div[1]/div[1]/div[2]/a",
                        )
                    )
                )
                break
            except:
                driver.refresh()
                sleep(1)
                continue

        # click on the first element of the search results table to get to the emails
        results_list = None
        rows = None
        while True:
            try:
                results_list = driver.find_element(By.CLASS_NAME, "search-results-list")
                rows = results_list.find_elements(By.TAG_NAME, "li")
                break
            except:
                driver.refresh()
                sleep(3)
                continue
        
        # get the first element, then click on it
        first_element = rows[0]
        print("First element HTML:")
        print(first_element.get_attribute("outerHTML"))
        while True:
            try:
                first_element = rows[0].find_element(By.CLASS_NAME, "profile-image-w[r]")
                break
            except:
                pass
            try:
                first_element = rows[0].find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/rr-unified-search-results/div/div[3]/div/ul/li[1]/rr-company-search-result/div/div[1]/div[1]/div[2]/a",
                ) 
            except:
                driver.refresh()
                sleep(1)
                continue
        first_element.click()

        # switch to new tab
        driver.switch_to.window(driver.window_handles[1])

        # Locate the email format tab
        while True:
            try:
                WebDriverWait(driver, timeout=10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div/div[3]/div[1]/div/ul/li[2]/a",
                        )
                    )
                )

                # click on email format tab
                driver.find_element(
                    By.XPATH, "/html/body/div[1]/div[7]/div/div[3]/div[1]/div/ul/li[2]/a"
                ).click()

                # Wait for the table to appear
                WebDriverWait(driver, timeout=10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div[7]/div/div[3]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/div/table",
                        )
                    )
                )

                WebDriverWait(driver, timeout=10).until(
                    EC.presence_of_element_located(
                        (
                            By.CLASS_NAME,
                            "rr-profile-contact-card",
                        )
                    )
                )
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div[7]/div/div[3]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/div/table/tbody",
                )
                tds = driver.find_elements(By.TAG_NAME, "td")
                break
            except:
                driver.refresh()
                sleep(3)
                continue

        # process rows of the table
        current_row = []
        for td in range(len(tds)):
            if len(current_row) == 3:
                email_formats.append(current_row)
                current_row = []

            while True:
                try:
                    current_row.append(tds[td].text)
                    break
                except:
                    driver.refresh()
                    # Wait for the table to appear
                    WebDriverWait(driver, timeout=10).until(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                "/html/body/div[1]/div[7]/div/div[3]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/div/table",
                            )
                        )
                    )
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[1]/div[7]/div/div[3]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/div/table/tbody",
                    )
                    tds = driver.find_elements(By.TAG_NAME, "td")

        new_id = await insert_format_todb.insertCompanyEmailFormat(
            email_formats, companies_ref
        )
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        print(email_formats)
    driver.quit()
    return email_formats


if __name__ == "__main__":
    companies = ["Datadog"]

    asyncio.run(getCompanyEmailFormats(companies))
