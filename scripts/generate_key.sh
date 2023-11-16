# Check if project id is available and ask user to input if not
if [[ -z "${PROJECT_ID}" ]]; then
    # Prompt the user for their GCP project ID and store it in a variable
    read PROJECT_ID"?Enter your GCP project ID: "
fi

CLOUDBUILD_SA=cloudbuild-sa@${PROJECT_ID}.iam.gserviceaccount.com
CLOUDBUILD_SA_KEY_FILETYPE="json"
CLOUDBUILD_SA_KEY_FILENAME="$PROJECT_ID-cloudbuild-sa-key.$CLOUDBUILD_SA_KEY_FILETYPE"

# Check if service account key file exists at the project root. If it doesn't create one
if [ ! -f "${CLOUDBUILD_SA_KEY_FILENAME}" ]; then
    # Check if project id is available and ask user to input if not

    gcloud iam service-accounts keys create $CLOUDBUILD_SA_KEY_FILENAME \
    --iam-account=$CLOUDBUILD_SA --key-file-type=$CLOUDBUILD_SA_KEY_FILETYPE --project=$PROJECT_ID

else
    echo "Cloudbuild service account key already exists at ${CLOUDBUILD_SA_KEY_FILENAME}"
fi

export CLOUDBUILD_SA=$CLOUDBUILD_SA
echo "CLOUDBUILD_SA: ${CLOUDBUILD_SA}"
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/${CLOUDBUILD_SA_KEY_FILENAME}"
echo "GOOGLE_APPLICATION_CREDENTIALS: ${GOOGLE_APPLICATION_CREDENTIALS}"
