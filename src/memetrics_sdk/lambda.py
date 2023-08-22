import json
import os

import requests

url = "https://us-east-1.aws.data.mongodb-api.com/app/data-eimra/endpoint/data/v1/action/insertOne"

document = {"event": ...}

payload = json.dumps(
    {
        "collection": "searchresult",
        "database": "datasources-osf",
        "dataSource": "wingman-prod",
        "document": document,
    }
)
headers = {
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*",
    "api-key": os.environ["MONGODB_API_KEY"],
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)  # '{ "insertedId": "63dc56ac74ddb86ed3eb8474" }'
