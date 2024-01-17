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
    url = f"https://{config.citystate}.workflow.opengov.com/"

    openGovScraper = OpenGovScraper(config.open_gov_username, config.open_gov_password)

    openGovScraper.login(url)

    logs = openGovScraper.get_logs()

    token = openGovScraper.get_api_token(logs)

    openGovScraper.quit_driver()

    category_id = openGovScraper.get_category_id(
        url,
        token,
        config.category,
    )

    report_payload = openGovScraper.get_report_payload(
        url,
        token,
        category_id,
        config.dataset,
    )

    headers_dict = openGovScraper.generate_report(
        f"https://api01.viewpointcloud.com/v2/{config.citystate}/reports/explore",
        token,
        config.dataset,
        report_payload,
    )

    output_object = {
        "status": "ok",
        "file_name": f"open_gov_puller/data/{config.dataset.lower().replace(' ', '_')}.csv",
        "columns": headers_dict,
    }

    print("DONE", json.dumps(output_object))


def load_config(file_path):
    raw_config = load_json(file_path)

    sub_config = raw_config.get("config", {})

    category = sub_config.get("category", None)
    dataset = sub_config.get("dataset", None)
    citystate = sub_config.get("citystate", None)

    open_gov_username = raw_config.get("env", None).get("open_gov_username", None)
    open_gov_password = raw_config.get("env", None).get("open_gov_password", None)

    return Config(
        category,
        dataset,
        citystate,
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
