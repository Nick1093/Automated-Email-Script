# ------------------------------------------------------------------------------------------------------------------------------ #
# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------------------------------------------------------------------------------------------------------------ #
# Pandas and openpyxl
import pandas as pd
import openpyxl

import os
# ------------------------------------------------------------------------------------------------------------------------------ #

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

# Initialize Firestore client
db = firestore.client()

# Load the excel file
excel_file = "/Users/mac/Desktop/Projects/Automated-Email-Script/Email Formats.xlsx"
df = pd.read_excel(excel_file)
# ------------------------------------------------------------------------------------------------------------------------------ #



# helper to create the format to put into the database
def createEmailFormat(format, company_part):
    delimeter = format.split("]")
    if len(delimeter) > 2:
        delimeter = delimeter[1][0] if delimeter[1][0] != "[" else ""
    else: 
        delimeter = ""

    # string play with the format
    format = format.replace("[", " ").replace("]", " ").split(" ")

    # format is of length 3 when there is only 1 field, when there is 2 - it is of length 5
    first = "{0[" + format[1] + "]}"
    second = "{2[" + format[-2] + "]}" if len(format) > 3 else ""

    final_format = first + delimeter + second + company_part

    return final_format



# Webscraping Algorithm
def insertCompanyEmailFormat():
    # email_format
    email_format = "{{0[first]}}{2[separator]}{{1[last]}}@{3[company]}"

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # initiate the connection to the collection
        companies_ref = db.collection('Companies')

        # Check if any of the required columns have missing values
        if row.isnull().all():
            # Skip this row because it has missing data
            continue
        
        # get the company name through string manipulation
        company_name = row[1].split('@')[1].split('.')[0]
        
        # get the company email part to make the format
        company_email_part = row[1].split('@')[1]

        # create the email with the format and get the accuracy
        try:
            email_format = createEmailFormat(row[0], company_email_part)
        except:
            print("Email format construction did not work!")
            continue

        accuracy = (row[2] * 100)

        # variable to store new format
        new_entry = {"email_format": email_format, "accuracy": accuracy}

        # check if we already put the company in the database
        query = companies_ref.where("name", "==", company_name.title()).limit(1)
        results = query.get()

        # if we got back results, something exists, so we insert it
        if results:
            # get the doc id to find the doc
            doc_id = results[0].id

            # get the ref to update by the id
            current_ref = db.collection('Companies').document(doc_id)

            # update the email_formats array to add the new format
            try:
                current_ref.update({"email_formats": firestore.ArrayUnion([new_entry])})
            except:
                print("Add did not work: ", company_name, new_entry)
            print("Add format: ", company_name, doc_id, )
        else:
            try:
                new_doc_id = companies_ref.add({"name": company_name.title(), "email_formats": [new_entry]})[1].id
            except:
                print("New Entry did not work: ", company_name, new_entry)
            print("New Entry: ", new_doc_id)

    return

insertCompanyEmailFormat()



