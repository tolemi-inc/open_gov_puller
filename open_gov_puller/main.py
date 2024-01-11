from open_gov_scraper import OpenGovScraper
from config import Config
from config_error import ConfigError
import argparse
import traceback
import json
import logging

parser = argparse.ArgumentParser(description="Process inputs for open gov pulls.")

parser.add_argument("--config", type=str, help="Path to config file")

args = parser.parse_args()

logging.getLogger().setLevel(logging.INFO)


def run(config):
    openGovScraper = OpenGovScraper(config.open_gov_username, config.open_gov_password)

    openGovScraper.login(config.login_url)

    logs = openGovScraper.get_logs()

    token = openGovScraper.get_api_token(logs)

    openGovScraper.quit_driver()

    with open("api_json/headers.json", "r") as json_file:
        headers = json.load(json_file)

    with open("api_json/headers2.json", "r") as json_file:
        headers2 = json.load(json_file)

    category_id = openGovScraper.get_category_id(
        config.login_url,
        token,
        headers2,
        config.category,
    )

    report_payload = openGovScraper.get_report_payload(
        config.login_url,
        token,
        headers2,
        category_id,
        config.dataset,
    )

    openGovScraper.generate_report(
        config.request_url,
        token,
        config.dataset,
        headers,
        report_payload,
    )


def load_config(file_path):
    raw_config = load_json(file_path)

    sub_config = raw_config.get("config", {})

    category = sub_config.get("category", None)
    dataset = sub_config.get("dataset", None)
    login_url = sub_config.get("login_url", None)
    request_url = sub_config.get("request_url", None)

    open_gov_username = raw_config.get("env", None).get("open_gov_username", None)
    open_gov_password = raw_config.get("env", None).get("open_gov_password", None)

    return Config(
        category,
        dataset,
        login_url,
        request_url,
        open_gov_username,
        open_gov_password,
    )


def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        True
        # print(f"File '{file_path}' not found.")
    except json.JSONDecodeError as e:
        True
        # print(f"JSON decoding error: {e}")
    except Exception as e:
        True
        # print(f"An error occurred: {e}")


def fail(error):
    result = {
        "status": "error",
        "error": """{}
         {}""".format(
            str(error), traceback.format_exc()
        ),
    }

    output_json = json.dumps(result)
    print("DONE", output_json)


if __name__ == "__main__":
    try:
        config = load_config(args.config)
        run(config)
    except ConfigError as e:
        fail(e)
