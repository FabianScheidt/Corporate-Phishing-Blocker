# pylint: disable=missing-module-docstring,missing-function-docstring
import sys
import os
import json
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


API_KEY = ""
DOMAIN_COMPANY = "Cofense"
DOMAIN_CONTENT_FILTER = "This was an authorized phishing simulation"


def print_usage():
    print("Collect and validate domains. Configure Outlook Web to block them.")
    print("")
    print("Run in order:")
    print("python3 main.py collect-domains")
    print("python3 main.py validate-domains")
    print("python3 main.py configure-outlook")


def collect_domains():
    """
    Fetches the list of domains and stores them in a json file.
    :return:
    """
    payload = {
        "apiKey": API_KEY,
        "mode": "purchase",
        "basicSearchTerms": {
            "include": [DOMAIN_COMPANY],
        },
    }
    res = requests.post("https://reverse-whois.whoisxmlapi.com/api/v2", json=payload)

    with open("domains.json", "w") as outfile:
        json.dump(res.json(), outfile, indent=4)


def validate_domains():
    """
    Performs a HTTP request to each of the previously fetched domains and checks if the response
    body contains the filter values. Stores the list of valid domains in a json file.
    :return:
    """
    if not os.path.exists("domains.json"):
        print("Domains don't seem to be collected. Run collection first.")
        sys.exit(1)

    with open("domains.json", "r") as domains_file:
        res = json.load(domains_file)

    domains_list = res["domainsList"]
    valid_domains = []

    for domain in sorted(domains_list):
        try:
            res = requests.get("http://" + domain, timeout=5)
            if DOMAIN_CONTENT_FILTER in res.text:
                print(f"Domain {domain} is valid")
                valid_domains.append(domain)
            else:
                print(f"Domain {domain} is not valid")
        except (requests.ConnectTimeout, requests.ConnectionError):
            print(f"Domain {domain} could not be validated")

    with open("valid-domains.json", "w") as outfile:
        json.dump(valid_domains, outfile, indent=4)


def configure_outlook():
    if not os.path.exists("valid-domains.json"):
        print(
            "Valid domains don't seem to be collected. Run collection and validation first."
        )
        sys.exit(1)

    driver = webdriver.Chrome()
    driver.get("https://outlook.office365.com/")
    print("Please sign in to Outlook Webapp!")

    # Open Settings
    settings = (By.ID, "owaSettingsButton")
    WebDriverWait(driver, 300).until(EC.presence_of_element_located(settings))
    driver.find_element(*settings).click()

    all_settings = (By.XPATH, "//*[contains(text(),'View all Outlook settings')]")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(all_settings))
    driver.find_element(*all_settings).click()

    rules_button = (By.XPATH, "//*[contains(text(),'Rules')]/ancestor::button")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(rules_button))
    time.sleep(10)  # Don't ask why...
    driver.find_elements(*rules_button)[-1].click()

    # Create the rule
    driver.implicitly_wait(10)
    driver.find_element(
        By.XPATH, "//*[contains(text(),'Add new rule')]/ancestor::button"
    ).click()
    driver.find_element(By.XPATH, "//*[contains(text(),'Select a condition')]").click()
    driver.find_element(
        By.XPATH, "//*[contains(text(),'Sender address includes')]"
    ).click()

    address_input = driver.find_element(
        By.XPATH, "//input[@placeholder='Enter all or part of an address']"
    )

    with open("valid-domains.json", "r") as valid_domains_file:
        domains = json.load(valid_domains_file)

    for domain in domains:
        address_input.send_keys("@" + domain + Keys.RETURN)

    print("Done! Finish your rule and then abort this script.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    elif sys.argv[1] == "collect-domains":
        print("Collecting Domains...")
        collect_domains()
    elif sys.argv[1] == "validate-domains":
        print("Validating Domains...")
        validate_domains()
    elif sys.argv[1] == "configure-outlook":
        print("Configuring Outlook. Once the browser has opened, please sign in.")
        configure_outlook()
    else:
        print_usage()
        sys.exit(1)
    print("Done!")
