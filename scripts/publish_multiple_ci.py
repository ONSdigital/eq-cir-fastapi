import datetime
import json
import os

from tests.integration_tests.utils import make_iap_request

path_to_json = "Enter your Folder location here"
post_url = "/v1/publish_collection_instrument"
timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
mandatory_keys = [
    "data_version",
    "classifier_type",
    "classifier_value",
    "language",
    "survey_id",
    "title",
    "description",
]
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


def load_ci_from_path(path_to_json):
    """
    This function loads CIs from the specified path and return ci_list and json file names
    """
    ci_list = []
    json_files = os.listdir(path_to_json)
    for json_file in json_files:
        with open(f"{path_to_json}/{json_file}") as content:
            ci = json.load(content)
            ci_list.append(ci)
    return ci_list, json_files


def publish_ci_file(ci, file_name, log_file, total_errors_found):
    """
    This function publishes ci and upon publish following things will be logged for each collection instrument
    to be published:
       1. File name.
       2. Response recieved.
       3. Missing Mandatory Fields(if response recieved has message `Field required`).
       4. Missing Optional Fields(if response recieved has the message `Field required`).
       5 Additonal Fields that are not present in the `PostCiMetadataV1PostData` model(if
       response recieved has the message `Field required`)).
    """
    ci_response = make_iap_request("POST", f"{post_url}", json=ci)
    ci_response = ci_response.json()
    if ci_response["message"] == "Field required" and ci_response["status"] == "error":
        total_errors_found += 1
        mandatory_missing_keys = [key for key in (mandatory_keys) if key not in ci]
        optional_missing_keys = [key for key in (optional_keys) if key not in ci]
        additional_keys = [key for key in ci if key not in (mandatory_keys + optional_keys)]
        log_file.write(
            f"CI File name: {file_name}\n"
            f"CI response {ci_response}\n"
            f"Mandatory Missing Fields {mandatory_missing_keys}\n"
            f"Optional Missing Fields {optional_missing_keys}\n"
            f"Additional Fields Found {additional_keys}\n\n\n"
        )
    elif ci_response["status"] == "error":
        total_errors_found += 1
        log_file.write(f"CI file name {file_name}\n" f"CI response {ci_response}\n\n")
    else:
        log_file.write(f"CI file name {file_name}\n" f"CI response {ci_response}\n\n")
    return total_errors_found


def process_ci_files(ci_list, json_files):
    """
    This function creates a log file which is used in storing responses in `publish_ci_file` function and provide
    consolidated count of json files to be published and errors found is provdied at the end of the log file
    """
    total_errors_found = 0
    with open(f"log_{timestamp}.log", "a") as log_file:
        for ci, file_name in zip(ci_list, json_files):
            total_errors_found = publish_ci_file(ci, file_name, log_file, total_errors_found)
        log_file.write(
            f"Folder location provided: {path_to_json}\n"
            f"Total Number of Json files to be published: {len(json_files)}\n"
            f"Total errors found total_errors_found: {total_errors_found}\n\n"
        )


if __name__ == "__main__":
    """
    Before running this file make sure to clone the required repository and then specify the path above
    """

    ci_list, json_files = load_ci_from_path(path_to_json)
    process_ci_files(ci_list, json_files)
