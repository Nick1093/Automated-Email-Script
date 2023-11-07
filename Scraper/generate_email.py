scraped_data = []

first, last, first_initial, last_initial = "", "", "", ""

formats = {"first": "", "last": "", "first_initial": "", "last_initial": ""}

# helper method to generate users emails
def generate_email(name, company, companies_ref):
    emails = []
    company = company.replace("@", "").replace("at", "")
    clist = company.split(" ")

    new_first = name.split(" ")[0]
    new_last = name.split(" ")[-1]
    new_first_initial = new_first[0]
    new_last_initial = new_last[0]

    formats["first"] = new_first
    formats["last"] = new_last
    formats["first_initial"] = new_first_initial
    formats["last_initial"] = new_last_initial

    for c in reversed(clist):
        query = companies_ref.where("name", "==", c).limit(1)
        results = query.get()

        if results:
            for result in results:
                data = result.to_dict()
                email_formats = data.get("email_formats", [])

                for template in email_formats:
                    email = template.get("email_format", "")  # Get the template string
                    email = email.format(formats, formats)
                    emails.append([email, float(template.get("accuracy"))])

    if not emails:
        # for template in potentials:
        #     print(template)
        #     emails.append(template.format(formats, formats, formats))

        return "Company not recognized in database"

    return emails