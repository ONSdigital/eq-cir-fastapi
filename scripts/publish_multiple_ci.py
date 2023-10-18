import urllib3

import json

# Set up your Firestore credentials
# You can obtain the credentials from your Google Cloud project
# and set the environment variable GOOGLE_APPLICATION_CREDENTIALS

# Set up your Firestore client


def download_and_store_json(urls):
    http = urllib3.PoolManager()

    for url in zip(urls):
        response = http.request('GET', url)
        
        if response.status == 200:
            # Parse JSON data
            json_content = response.data.decode('utf-8')
            data = json.loads(json_content)
            print(data)

if __name__ == "__main__":
    # Replace these with your actual public URLs and corresponding document IDs
    download_and_store_json("https://github.com/ONSdigital/eq-questionnaire-schemas/tree/main/schemas/business/en")



