# eq-collection-instrument-registry

This project is Collection Instrument Registry. It will manage the storage and versioning of Electronic Questionnaires used but the EQ services. It uses the [FastAPI](https://fastapi.tiangolo.com/) Python web framework.

## Project requirements and initial setup

This project has the following dependencies:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Rancher Desktop](https://rancherdesktop.io/)
- [google-cloud-sdk](https://cloud.google.com/sdk)
- [pyenv](https://github.com/pyenv/pyenv)

You will also need a Google Cloud account with the relevant permissions to create projects within the ONS Digital project.

To install dependencies and configure the project for first use, follow the instructions below:

1. If required, install either Docker Desktop or Rancher Desktop
2. Open a terminal at the project root
3. Install other dependencies using `brew`

   `$ brew upgrade && brew install google-cloud-sdk pyenv`

4. Install and start using the Python version defined in the `.python-version` file using `pyenv`

   `$ pyenv install`

5. Create a new virtual environment to manage Python packages for the project using `venv` and activate it

   `$ python3 -m venv env && source env/bin/activate`

6. Install project requirements using `pip`. This action will read the attributes in the `requirements.txt` file and install the right packages and versions we need, which insures we can set the correct dependencies for other devs and when deploying to production

   `$ pip install --upgrade pip && pip install -r requirements.txt`

The project is now ready for development or to use for deployments.

### Setting up GPG Key

- For signing commits to the git repository, create a new GPG key if you don't have an existing key. Follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key) for creating a new GPG Key
- For the adding the new key to the account, follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account)
- For telling Git about the Signing Key(Only needed once),follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key)

## Running the application locally

We can build and run the FastAPI application, including emulators for firestore and cloud storage, locally for testing. To build and run the application for testing, follow the instructions below:

1. Start your Docker container manager (Docker Desktop or Rancher Desktop)
2. Open a terminal at the project root
3. Build the Docker containers for the FastAPI application and emulators

   `$ docker-compose build`

4. Start the Docker containers

   `$ docker-compose up`

The FastAPI application will now be running and available at the host `0.0.0.0:3030`. You can use the interactive Swagger docs at `0.0.0.0:3030/docs`.

## Running the application locally with services running in GCloud

In order to connect to real services in GCloud, you will need a GCP test project or make
use of the sandbox project. Instructions for setting this up are included in the IaC repo.

Once you have setup your project, you will need a key file to allow CIR to talk to bucket storage
and the database. To create one:

- Go the IAM page and select Service accounts
- Create a new service account
- Call it "test"
- Add the roles that are needed for testing
- Go into service account and create a key. This will download a JSON file to your machine
- Copy the downloaded JSON file to this directory and rename to `key.json`

To run CIR locally, activate the virtual environment, then run the following commands (ensuring that the values in the
makefile represent the connections you wish to make):

```bash
make start-cloud-dev
```

## Deploying the application containers for testing

We can deploy the Collection Instrument Registry container to a project within the `cir-sandbox` GCP project for development and testing. You will need a cloud project configured for the Collection Instrument Registry to do this.

### Creating a Google Cloud project

If you don't already have a project, see the instructions on how to create one in the [EQ Collection Instrument Registry IAC](https://github.com/ONSdigital/eq-collection-instrument-registry-iac) repository. Make a note of the `project_id` for use later.

### Url routing

The terraform script used to provision your project in the step above will set up routing from the host and authentication using a Load Balancer and Identity Aware Proxy (IAP). The url routes for your application as managed by FastAPI as part of the routes defined in `app/main.py`.

### Deploying the container

Once you have a Google Cloud project including a Load Balancer and Identity Aware Proxy (IAP) configuration, we can build and push our container to the cloud using the `./scripts/deploy_to_dev_project.sh` script. This will build and push the Docker container and create an auth key required for integration testing.
To deploy cloud functions for testing, follow the instructions below:

1. Start your Docker container manager (Docker Desktop or Rancher Desktop)
2. Open a terminal at the project root
3. Authenticate with Google Cloud

   `$ gcloud auth application-default login`

4. Execute the script and follow the instructions. Note that this could take up to 5 minutes!

   `$ source ./scripts/deploy_to_dev_project.sh`

When this script has completed, it will export values for the following environment variables:

- BUILD_ID
- CI_STORAGE_BUCKET_NAME
- DEFAULT_HOSTNAME
- GOOGLE_APPLICATION_CREDENTIALS
- OAUTH_CLIENT_ID
- PROJECT_ID
- URL_SCHEME

These variables will be configured to work with the project the Docker image was deployed to and the Load Balancer and IAP. These can then be used when debugging and running tests (e.g. when running `make integration-tests`).

`GOOGLE_APPLICATION_CREDENTIALS` and `OAUTH_CLIENT_ID` are required to generate an auth token to authenticate requests with the IAP when running integration tests. See the `make_iap_request` code in `tests/integration_tests/utils/utils.py` for more details.

If you want to test posting data to these functions using Postman or similar, you should use a url constructed using the `DEFAULT_HOSTNAME` variable value with an appropriate http schema and endpoint e.g. `https://<DEFAULT_HOSTNAME>/v1/publish_collection_instrument`. You will need to generate an auth token to authenticate with these endpoints, see the `make_iap_request` code in `tests/integration_tests/utils/utils.py`.

## Testing

### Integration testsing

### Everything running in the cloud

In this configuration, the integration test uses the CIR API service running in Cloud Run of your test/dev GCP project. Please note that the CIR is not the updated version unless run after either executing the deploy script or creating a PR and gone through the pipeline. These services both talk to Firestore and Cloud Storage running on the same project.

```bash
PROJECT_NAME=ons-sds-sandbox-01
gcloud auth login
gcloud config set project $PROJECT_NAME

make integration-test-sandbox
```

### Unit testing

To run unit tests from root folder run `make unit-tests`

## Linting

To run the linter on the project, run `make lint`. This will have to be ran in order for the build to be successful.

## The openapi spec document

The openapi spec file in `gateway/openapi.yaml` should not be edited manually as it can be autogenerated using FastAPI utilities. This file should be regenerated every time the app changes. To autogenerate the file run `make generate-spec`.

## Publishing bulk CIs

Multiple CIs can be published using `scripts/publish_multiple_ci.py`. To run the file run `make publish-multiple-ci`.A Log file
will be generated with timstamp once all the CIs are published.Before running, make sure to clone the [eq-questionnaire-schemas](https://github.com/ONSdigital/eq-questionnaire-schemas/tree/main/schemas/business/en) repository and specify the file location in `publish_multiple_ci.py`.

## Running in docker

You will have to add code to create a topic adding the following snippet to publisher.py and calling it in function _verify_topic_exists.
Remember not to accidentally commit.

```python
def create_topic(self) -> None:
   """Create a new Pub/Sub topic."""
   logger.debug("create_topic")
   topic = self.publisher_client.create_topic(request={"name": self.topic_path})
   logger.debug(f"Created topic: {topic.name}")
```