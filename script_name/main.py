from open_gov_scraper import OpenGovScraper
import os
from dotenv import load_dotenv
import json

load_dotenv()

openGovScraper = OpenGovScraper(
    os.getenv("OPENGOV_USERNAME"), os.getenv("OPENGOV_PASSWORD")
)

openGovScraper.login(os.getenv("LOGIN_URL"))

logs = openGovScraper.get_logs()

token = openGovScraper.get_api_token(logs)

openGovScraper.quit_driver()

with open("api_json/reports.json", "r") as json_file:
    reports = json.load(json_file)

with open("api_json/headers.json", "r") as json_file:
    headers = json.load(json_file)

with open("api_json/payload.json", "r") as json_file:
    payload = json.load(json_file)

openGovScraper.generate_reports(
    token, os.getenv("REQUEST_URL"), reports, headers, payload
)
