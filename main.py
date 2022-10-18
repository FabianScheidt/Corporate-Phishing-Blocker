# pylint: disable=missing-module-docstring,missing-function-docstring
import sys
import os
import json

import requests


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
    raise NotImplementedError


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
