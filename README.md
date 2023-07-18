# eq-collection-instrument-registry
This project is Collection Instrument Registry. It will manage the storage and versioning of Electronic Questionnaires used but the EQ services. It uses the [FastAPI](https://fastapi.tiangolo.com/) Python web framework.

## Project requirements and initial setup
This project has the following dependencies:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Rancher Desktop](https://rancherdesktop.io/)
* [google-cloud-sdk](https://cloud.google.com/sdk)
* [pipenv](https://pipenv.pypa.io/en/latest/)
* [pyenv](https://github.com/pyenv/pyenv)

You will also need a Google Cloud account with the relevant permissions to create projects within the ONS Digital project.

To install dependencies and configure the project for first use, follow the instructions below:
1. If required, install either Docker Desktop or Rancher Desktop
2. Open a terminal at the project root
3. Install other dependencies using `brew`

   ```$ brew upgrade && brew install google-cloud-sdk pipenv pyenv```
4. Install the Python version defined in the `.python-version` file using `pyenv`

   ```$ pyenv install```
5. Set the Python version we want to use, if not already done by the installation

   ```$ pyenv use $(cat .python-version)```
6. Create a new virtual environment to manage Python packages for the project. This action will read the attributes in the `Pipfile` and `Pipfile.lock` and install the right packages and versions we need, which insures we can set the correct dependencies for other devs and when deploying to production

   ```$ pipenv install --dev```
7. Activate your newly created virtual environment by running

   ```$ pipenv shell```

The project is now ready for development or to use for deployments.

### Setting up GPG Key
* For signing commits to the git repository, create a new GPG key if you don't have an existing key. Follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key) for creating a new GPG Key
* For the adding the new key to the account, follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account)
* For telling Git about the Signing Key(Only needed once),follow the [link](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key)

## Testing

### Unit testing
To run unit tests from root folder run `make unit-tests`

## Linting
To run the linter on the project, run ```make lint```. This will have to be ran in order for the build to be successful.
