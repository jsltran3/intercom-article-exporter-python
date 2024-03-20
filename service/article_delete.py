import os
import requests
import csv
import articles_importer
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
INTERCOM_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')

def delete_articles_with_no_parent(access_token):
    url = "https://api.intercom.io/articles"
    headers = {
        "Intercom-Version": "2.10",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Get all articles from the source organization
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'data' in data:
        articles = data['data']
        for article in articles:
            if 'parent' not in article or article['parent']['type'] == 'nul':  # Check if parent_id is missing or null
                article_id = article['id']
                delete_url = f"{url}/{article_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 204:
                    print(f"Article with ID {article_id} deleted successfully.")
                else:
                    print(f"Error deleting article with ID {article_id}: {delete_response.json()}")
            else:
                print(f"Skipping article with ID {article['id']} as it has a parent.")

    else:
        print("Error fetching articles:", data)

if __name__ == "__main__":
    if INTERCOM_TOKEN:
        delete_articles_with_no_parent(INTERCOM_TOKEN)
    else:
        print("Source Intercom access token not found in .env file.")
