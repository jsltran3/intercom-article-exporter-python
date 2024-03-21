import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
INTERCOM_ACCESS_TOKEN = os.getenv('SOURCE_INTERCOM_ACCESS_TOKEN')

def list_help_centers(access_token):
    url = "https://api.intercom.io/help_center/help_centers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('help_centers', [])
    else:
        print(f"Error fetching help centers: {response.status_code} - {response.json()}")
        return []

def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    if INTERCOM_ACCESS_TOKEN:
        help_centers = list_help_centers(INTERCOM_ACCESS_TOKEN)

        if help_centers:
            export_to_csv(help_centers, 'intercom_help_centers.csv')
            print("Help centers exported to intercom_help_centers.csv")
        else:
            print("No help centers found.")
    else:
        print("Intercom access token not found in .env file.")
