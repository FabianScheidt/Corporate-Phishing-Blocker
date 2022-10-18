# Corporate Phishing Blocker

Corporations regularly send phishing test emails to their employees, who are in turn asked to flag these as phishing.
Internal metrics track how many employees pass this tests, and everybody sleeps better if the metric is good.

In an attempt to raise these performance metrics, this is a script to collect domain names from services like _Cofense_,
validate if they are used for phishing tests and configure the validated domains to be automatically blocked using
rules in Outlook Web.

## Usage

Create a Conda environment and get an API key from whoisxmlapi.com. Enter the API key in _main.py_ and run the following
commands to fetch and validate the domain names:

```shell
python3 main.py collect-domains
python3 main.py validate-domains
```

Run the below command to help you with the configuration of a rule in Outlook Web. It will open a browser and
automatically fill in the domain names. Make sure you have Chrome and Chromedriver installed.

```shell
python3 main.py configure-outlook
```

## Disclaimer

Obviously, this solution undermines the good intention to sensitize to the danger imposed by phishing and the proper
handling of it. This is just a technical proof-of-concept. It is not recommended to actually use it!
