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
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run(config):
    logging.info("Running Python Script")

    url = f"https://{config.citystate}.workflow.opengov.com"

    openGovScraper = OpenGovScraper(config.open_gov_username, config.open_gov_password, config.citystate)

    openGovScraper.open_opengov(url)
    openGovScraper.login(url)
    openGovScraper.quit_driver()

    category_id = openGovScraper.get_category_id(
        url,
        config.category,
    )

    report_metadata = openGovScraper.get_report_metadata(url, category_id, config.dataset)

    report_payload = openGovScraper.generate_report_payload(
        report_metadata,
        category_id,
        config.dataset,
    )

    headers_dict = openGovScraper.generate_report(
        f"https://api-east.viewpointcloud.com/v2/{config.citystate}/reports/explore",
        report_payload,
        report_metadata,
        config.data_file_path
    )

    output_object = {
        "status": "ok",
        "file_name": config.data_file_path,
        "columns": headers_dict,
    }

    print("DONE", json.dumps(output_object))


def load_config(file_path):
    raw_config = load_json(file_path)

    data_file_path = raw_config.get('dataFilePath', None)

    sub_config = raw_config.get("config", {})
    category = sub_config.get("category", None)
    dataset = sub_config.get("dataset", None)
    citystate = sub_config.get("citystate", None)
    username = sub_config.get("open_gov_username", None)
    password = sub_config.get("open_gov_password", None)

    return Config(
        data_file_path,
        category,
        dataset,
        citystate,
        username,
        password,
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