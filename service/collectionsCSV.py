import os
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
INTERCOM_ACCESS_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')

def list_collections(access_token):
    url = "https://api.intercom.io/help_center/collections"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error fetching collections: {response.status_code} - {response.json()}")
        return []

def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'description', 'created_at', 'updated_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    if INTERCOM_ACCESS_TOKEN:
        collections = list_collections(INTERCOM_ACCESS_TOKEN)

        if collections:
            # Generate timestamp for today's date
            timestamp = datetime.now().strftime('%Y-%m-%d')

            # Export collections to CSV file
            export_to_csv(collections, f'intercom_collections_{timestamp}.csv')
            print(f"Collections exported to intercom_collections_{timestamp}.csv")
        else:
            print("No collections found.")
    else:
        print("Intercom access token not found in .env file.")
