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

    with open("api_json/reports.json", "r") as json_file:
        reports = json.load(json_file)

    with open("api_json/headers.json", "r") as json_file:
        headers = json.load(json_file)

    with open("api_json/payload.json", "r") as json_file:
        payload = json.load(json_file)

    openGovScraper.generate_report(
        token,
        config.request_url,
        config.dataset,
        config.dataset_id,
        config.base_columns + config.additional_columns,
        headers,
        payload,
    )


def load_config(file_path):
    raw_config = load_json(file_path)

    data_file_path = raw_config.get("dataFilePath", None)

    sub_config = raw_config.get("config", {})

    dataset = sub_config.get("dataset", None)
    dataset_id = sub_config.get("dataset_id", None)
    base_columns = sub_config.get("base_columns", None)
    additional_columns = sub_config.get("additional_columns", None)
    login_url = sub_config.get("login_url", None)
    request_url = sub_config.get("request_url", None)

    open_gov_username = raw_config.get("env", None).get("open_gov_username", None)
    open_gov_password = raw_config.get("env", None).get("open_gov_password", None)

    return Config(
        dataset,
        dataset_id,
        base_columns,
        additional_columns,
        login_url,
        request_url,
        data_file_path,
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
