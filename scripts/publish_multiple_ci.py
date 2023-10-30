import datetime
import json
import os

from tests.integration_tests.utils import make_iap_request

path_to_json = "/Users/sriparupudi/Desktop/work1/eq-questionnaire-schemas/schemas/business/en"
json_files = [pos_json for pos_json in os.listdir(path_to_json)]
post_url = "/v1/publish_collection_instrument"
total_errors_found = 0
timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
mandatory_keys = ["data_version", "form_type", "language", "survey_id", "title", "schema_version", "description"]
optional_keys = [
    "legal_basis",
    "metadata",
    "mime_type",
    "navigation",
    "questionnaire_flow",
    "post_submission",
    "sds_schema",
    "sections",
    "submission",
    "theme",
]


if __name__ == "__main__":
    """
    Before running this file make sure to clone the required repository and then specify the path above
    Upon publish following things will be logged for each collection instrument to be published:
    1. File name.
    2. Response recieved.
    3. Missing Mandatory Fields(if response recieved has message `Field required`).
    4. Missing Optional Fields(if response recieved has the message `Field required`).
    5 Additonal Fields that are not present in the `PostCiMetadataV1PostData` model(if
    response recieved has the message `Field required`)).
    A consolidated count of json files to be published and errors found is provdied at the end of the log file
    """
    print("::Publishing CI::")
    with open(f"log_{timestamp}.log", "a") as log_file:
        for json_file in json_files:
            with open(f"{path_to_json}/{json_file}") as content:
                ci = json.load(content)
                ci_response = make_iap_request("POST", f"{post_url}", json=ci)
                ci_response = ci_response.json()
                if ci_response["message"] == "Field required" and ci_response["status"] == "error":
                    total_errors_found += 1
                    mandatory_missing_keys = [key for key in (mandatory_keys) if key not in ci.keys()]
                    optional_missing_keys = [key for key in (optional_keys) if key not in ci.keys()]
                    additional_keys = [key for key in ci.keys() if key not in (mandatory_keys + optional_keys)]
                    log_file.write(
                        f"CI File name: {json_file}\n"
                        f"CI response {ci_response}\n"
                        f"Mandatory Missing Fields {mandatory_missing_keys}\n"
                        f"Optional Missing Fields {optional_missing_keys}\n"
                        f"Additional Fields Found {additional_keys}\n\n\n"
                    )

                elif ci_response["status"] == "error":
                    total_errors_found += 1
                    log_file.write(f"CI file name {json_file}\n" f"CI response {ci_response}\n\n")
                else:
                    log_file.write(f"CI file name {json_file}\n" f"CI response {ci_response}\n\n")
        log_file.write(
            f"Folder location provided: {path_to_json}\n"
            f"Total Number of Json files to be published: {len(json_files)}\n"
            f"Total errors found total_errors_found: {total_errors_found}\n\n"
        )
