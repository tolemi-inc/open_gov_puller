from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import json
import csv
import requests


class OpenGovScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        options = webdriver.ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.add_argument("headless")
        options.add_argument("--ignore-certificate-errors")
        service = webdriver.ChromeService(executable_path="chromedriver.exe")

        self.driver = webdriver.Chrome(
            service=service,
            options=options,
        )

    def login(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 30)
        login_username = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
        login_username.send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.CLASS_NAME, "auth0-lock-submit").click()
        logging.info("Logging In")
        try:
            inbox = wait.until(
                EC.presence_of_element_located((By.ID, "sidebar-inbox-btn"))
            )
            if inbox:
                logging.info("Login Successful")
        except:
            failure = self.driver.find_element(By.CLASS_NAME, "auth0-global-message")
            if failure:
                logging.error("Login Failed - invalid username or password")
                raise Exception("Error logging in")
            else:
                raise Exception("Error logging in")

    def get_logs(self):
        try:
            return self.driver.get_log("performance")
        except:
            raise Exception("Error getting chrome logs")

    def get_api_token(self, logs):
        try:
            for log in logs:
                json_log = json.loads(log["message"])["message"]

                if (
                    "params" in json_log
                    and "headers" in json_log["params"]
                    and ":path" in json_log["params"]["headers"]
                    and "authorization" in json_log["params"]["headers"]
                    and json_log["params"]["headers"][":path"]
                    == "/v2/mountvernonny/notifications/total_unread_count"
                ):
                    token = json_log["params"]["headers"]["authorization"]
                    logging.info("Found api token")
                    return token

            logging.error("Unable to find api token in chrome logs")

        except:
            raise Exception("Error getting api token")

    def quit_driver(self):
        logging.info("Quitting Selenium WebDriver")
        self.driver.quit()

    def get_category_id(self, url, token, headers, category_name):
        full_url = f"{url}/categories"
        headers["authorization"] = token
        response = requests.request("GET", full_url, headers=headers)

        category_id = next(
            (
                category["id"]
                for category in response.json()["categories"]
                if category["name"].strip() == category_name
            ),
            None,
        )

        return category_id

    def get_report_payload(self, url, token, headers, category_id, report_name):
        full_url = f"{url}/reports?categoryID={category_id}"
        headers["authorization"] = token
        response = requests.request("GET", full_url, headers=headers)

        matching_report = next(
            (
                report
                for report in response.json()["reports"]
                if report["name"] == report_name
                and report["createdByUserID"] == "auth0|652009d2a02a8ba6ec8cd878"
            ),
            None,
        )

        payload = {}
        if matching_report:
            payload["categoryID"] = category_id
            payload["recordTypeId"] = matching_report["recordTypeID"]
            payload["filters"] = "[]"
            payload["columns"] = matching_report["columns"]
            payload["reportType"] = 1
            payload["pageNumber"] = 0
            payload["fetchNumber"] = 50

        return payload

    def request_data(self, url, token, headers, payload):
        headers["authorization"] = token

        try:
            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(payload)
            )

            logging.info(
                "Response: " + str(response.status_code) + ", " + response.reason
            )

            if response.status_code == 200:
                return response.json()["data"]

            else:
                logging.error("Api request returned a non-200 response")
                raise Exception("Error making api request")

        except:
            raise Exception("Error making api request")

    def create_csv(self, data, path):
        try:
            with open(f"open_gov_puller/data/{path}", "w", newline="") as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for record in data:
                    writer.writerow(record)

                logging.info("Successfully created csv file")
        except:
            raise Exception("Error writing to csv file")

    def generate_report(self, url, token, dataset, headers, payload):
        csv_file_path = dataset.lower().replace(" ", "_") + ".csv"
        response_data = self.request_data(url, token, headers, payload)
        self.create_csv(response_data, csv_file_path)
