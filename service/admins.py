import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

INTERCOM_ACCESS_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')

def get_admins(access_token):
    url = "https://api.intercom.io/admins"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if 'admins' in data:
        return data['admins']
    else:
        print("Failed to fetch admins:", data)
        return None

def export_to_csv(admins, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'email', 'name', 'role', 'created_at', 'updated_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for admin in admins:
            writer.writerow({
                'id': admin.get('id', ''),
                'email': admin.get('email', ''),
                'name': admin.get('name', ''),
                'role': admin.get('role', ''),
                'created_at': admin.get('created_at', ''),
                'updated_at': admin.get('updated_at', ''),
            })

if __name__ == "__main__":
    admins = get_admins(INTERCOM_ACCESS_TOKEN)

    if admins:
        export_to_csv(admins, 'intercom_admins.csv')
        print("Admins exported to intercom_admins.csv")
    else:
        print("Error fetching admins.")
