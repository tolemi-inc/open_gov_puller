from playwright.sync_api import sync_playwright
import logging
import json
import csv
import requests
import time

class OpenGovScraper:
    def __init__(self, username, password, city_state):
        self.username = username
        self.password = password
        self.city_state = city_state
        self.api_token = None

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True,
            args=['--no-zygote'])
        self.page = self.browser.new_page()
    
    def open_opengov(self, url):
        self.page.on("response", lambda response: self.extract_api_token(response))
        self.page.goto(url)
        logging.info(f"Navigating to {url}")

    def login(self):
        # self.retry_wait_for_selector("input[name='email']")
        logging.info("Looking for email element")
        self.page.wait_for_selector("input[name='email']", timeout=100000)
        logging.info("Found email element")
        self.page.locator("input[name='email']").fill(self.username)
        self.page.locator("input[name='password']").fill(self.password)
        self.page.locator("xpath=//button[@type='submit']").click()
        logging.info("Logging in")
        try:
            inbox = self.page.wait_for_selector('#openGovLogo', timeout=100000)
            if inbox:
                logging.info("Login Successful")
            if self.api_token is None:
                raise Exception("Could not find API Token")
        except: 
            failure = self.page.wait_for_selector('.auth0-global-message', timeout=100000)
            if failure:
                logging.error("Login Failed - invalid username or password")
                raise Exception("Error logging in")
            else:
                raise Exception("Error logging in")
            
    def retry_wait_for_selector(self, selector, timeout=100000, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                return self.page.wait_for_selector(selector, timeout=timeout)
            except:
                logging.warning(f"Retrying to find {selector} - Attempt {attempt + 1}")
                attempt += 1
                time.sleep(2)
        raise Exception(f"Failed to find {selector} after {retries} attempts")
    
    def extract_api_token(self, response):
        if response.url == 'https://accounts.viewpointcloud.com/oauth/token':
            logging.info('API Token Found')
            self.api_token = response.json().get('access_token')

    def quit_driver(self):
        logging.info("Quitting Playwright Browser")
        self.browser.close()
        self.playwright.stop()

    def make_api_call(self, method, url, headers, payload=None):
        try:
            if payload:
                response = requests.request(
                    method, url, headers=headers, data=json.dumps(payload)
                )
            else:
                response = requests.request(method, url, headers=headers)

            logging.info(
                "Response: " + str(response.status_code) + ", " + response.reason
            )

            if response.status_code == 200:
                return response

            else:
                logging.error("Api request returned a non-200 response")
                raise Exception("Error making api request")

        except:
            raise Exception("Error making api request")

    def get_category_id(self, url, category_name):
        full_url = f"{url}/categories"
        headers = {"authorization": f"Bearer {self.api_token}", "subdomain": self.city_state}

        response = self.make_api_call("GET", full_url, headers)
        logging.info(
            f"Successfully found id for category named {category_name} from OpenGov"
        )

        category_id = next(
            (
                category["id"]
                for category in response.json()["categories"]
                if category["name"].strip() == category_name
            ),
            None,
        )

        return category_id

    def get_report_payload(self, url, category_id, report_name):
        full_url = f"{url}/reports?categoryID={category_id}"
        headers = {"authorization": f"Bearer {self.api_token}", "subdomain": self.city_state}

        response = self.make_api_call("GET", full_url, headers)
        logging.info(
            f"Successfully found report metadata for category with id {category_id} from OpenGov"
        )

        matching_report = next(
            (
                report
                for report in response.json()["reports"]
                if report["name"] == report_name
                # and report["createdByUserID"] == "auth0|652009d2a02a8ba6ec8cd878"
            ),
            None,
        )
        
        payload = {}
        if matching_report:
            payload["categoryID"] = category_id
            payload["recordTypeID"] = matching_report["recordTypeID"]
            payload["filters"] = "[]"
            payload["columns"] = matching_report["columns"]
            payload["reportType"] = matching_report["reportScopeID"]
            payload["pageNumber"] = 0
            payload["fetchNumber"] = 50
            logging.info(f"Successfully found report metadata for report named {report_name}")
        else:
            logging.info(f"No report named {report_name} found")

        return payload

    def request_data(self, url, payload):
        headers = {"authorization": f"Bearer {self.api_token}", "content-type": "application/vnd.api+json"}
        response = self.make_api_call("POST", url, headers, payload)
        logging.info(
            f"Successfully retrieved data for report with id {payload['recordTypeID']} from OpenGov"
        )

        return response.json()["data"]

    def create_csv(self, data, path):
        try:
            with open(f"open_gov_puller/{path}", "w", newline="") as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for record in data:
                    writer.writerow(record)

                logging.info("Successfully created csv file")

                return fieldnames
        except:
            raise Exception("Error writing to csv file")

    def generate_report(self, url, payload, path):
        response_data = self.request_data(url, payload)
        headers = self.create_csv(response_data, path)

        headers_dict = [{"name": header, "type": "VARCHAR"} for header in headers]

        return headers_dict
