from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        try:
            inbox = wait.until(EC.presence_of_element_located((By.ID, "inbox-topbar")))
            if inbox:
                print("Login Successful")
        except:
            failure = self.driver.find_element(
                By.CLASS_NAME, "auth0-global-message-error"
            )
            if failure:
                print("Login Failed")

    def get_logs(self):
        return self.driver.get_log("performance")

    def get_api_token(self, logs):
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
                return json_log["params"]["headers"]["authorization"]

    def quit_driver(self):
        print("Quitting Selenium WebDriver")
        self.driver.quit()

    def request_data(self, url, token, report, headers, payload):
        payload["recordTypeID"] = report["record_type_id"]
        # payload["columns"] = report["columns"]
        updated_payload = json.dumps(payload)

        headers["authorization"] = token

        response = requests.request("POST", url, headers=headers, data=updated_payload)

        print(response)
        response_data = response.json()["data"]

        return response_data

    def create_csv(self, data, path):
        with open(f"data/{path}", "w", newline="") as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for record in data:
                writer.writerow(record)

    def generate_reports(self, token, url, reports, headers, payload):
        for report in reports:
            csv_file_path = report["name"] + ".csv"
            response_data = self.request_data(url, token, report, headers, payload)
            self.create_csv(response_data, csv_file_path)
