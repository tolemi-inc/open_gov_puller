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

    def login(self, url):
        logging.info("Looking for email element")
        try:
            self.retry_wait_for_selector(url, "input[name='email']")
        except:
            print(self.page.content())
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
            
    def retry_wait_for_selector(self, url, selector, timeout=50000, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                self.page.goto(url)
                logging.info(f"Navigating to {url}")
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
    
    def get_report_metadata(self, url, category_id, report_name):
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
                if report["name"] == report_name and report["categoryID"] == category_id
            ),
            None,
        )

        return matching_report

    def generate_report_payload(self, report_metadata, category_id, report_name):
        payload = {}
        if report_metadata:
            payload["categoryID"] = category_id
            payload["recordTypeID"] = report_metadata["recordTypeID"]
            payload["filters"] = report_metadata["filters"]
            payload["columns"] = report_metadata["columns"]
            payload["reportType"] = report_metadata["reportScopeID"]
            payload["pageNumber"] = 0
            payload["fetchNumber"] = 500000
            logging.info(f"Successfully found report metadata for report named {report_name}")
        else:
            logging.info(f"No report named {report_name} found")

        return payload
    
    def create_column_name_mapping(self, columns):
        updated_column_names = {}
        for col in columns:
            if 't' in col and 'c' in col:
                updated_column_names[f"{col['t']}{col['c']}"] = col['n'].replace(' ', '_')
            if 'ffID' in col:
                updated_column_names[str(col['ffID'])] = col['n'].replace(' ', '_')
        return updated_column_names
    
    def update_column_names(self, data, report_metadata):
        column_names = self.create_column_name_mapping(json.loads(report_metadata["columns"]))
        renamed_data = []
        for record in data:
            new_record = {}
            for key, value in record.items():
                # Use the mapping to rename the keys
                new_key = column_names.get(key, key)  # Default to the original key if no mapping found
                new_record[new_key] = value
            renamed_data.append(new_record)

        return renamed_data

    def request_data(self, url, payload):
        headers = {"authorization": f"Bearer {self.api_token}", "content-type": "application/vnd.api+json"}
        more_data = True
        page_number = 0
        page_size = 10000
        full_data = []

        while more_data:
            payload["pageNumber"] = page_number
            payload["fetchNumber"] = page_size
            response = self.make_api_call("POST", url, headers, payload)

            response_data = response.json().get("data", [])
            full_data.extend(response_data)
            logging.info(f"Retrieved {len(response_data)} records from page {page_number}")
            
            if len(response_data) < page_size:
                more_data = False

            page_number += 1

        logging.info(f"Successfully retrieved data for report with id {payload['recordTypeID']} from OpenGov")
        return full_data

    def create_csv(self, data, path):
        try:
            with open(path, "w", newline="") as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames = fieldnames)

                for record in data:
                    writer.writerow(record)

                logging.info("Successfully created csv file")

                return fieldnames
        except:
            raise Exception("Error writing to csv file")

    def generate_report(self, url, payload, report_metadata, path):
        response_data = self.request_data(url, payload)
        updated_response_data = self.update_column_names(response_data, report_metadata)
        headers = self.create_csv(updated_response_data, path)

        headers_dict = [{"name": header, "type": "VARCHAR"} for header in headers]

        return headers_dict