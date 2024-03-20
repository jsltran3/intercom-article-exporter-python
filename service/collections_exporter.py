import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SOURCE_ACCESS_TOKEN = os.getenv('SOURCE_INTERCOM_ACCESS_TOKEN')
TARGET_ACCESS_TOKEN = os.getenv('TARGET_INTERCOM_ACCESS_TOKEN')

def retrieve_collections(access_token):
    url = "https://api.intercom.io/collections"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('collections', [])
    else:
        print(f"Error fetching collections: {response.json()}")
        return []

def create_collection(access_token, collection_data):
    url = "https://api.intercom.io/collections"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=collection_data)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"Error creating collection: {response.json()}")
        return None

if __name__ == "__main__":
    if SOURCE_ACCESS_TOKEN and TARGET_ACCESS_TOKEN:
        # Retrieve collections from source account
        source_collections = retrieve_collections(SOURCE_ACCESS_TOKEN)

        # Create collections in target account
        for collection in source_collections:
            collection_data = {
                "name": collection.get('name', ''),
                "description": collection.get('description', ''),
                "color": collection.get('color', ''),
                "icon": collection.get('icon', ''),
                "collection_order": collection.get('collection_order', 0),
                "app_id": collection.get('app_id', ''),
                "type": collection.get('type', '')
            }

            new_collection_id = create_collection(TARGET_ACCESS_TOKEN, collection_data)
            if new_collection_id:
                print(f"Collection '{collection['name']}' created in target account with ID: {new_collection_id}")
            else:
                print(f"Error creating collection '{collection['name']}' in target account.")
    else:
        print("Source or target Intercom access token not found in .env file.")
