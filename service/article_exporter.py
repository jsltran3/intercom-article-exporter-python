import os
import requests
import csv
import articles_importer
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SOURCE_ACCESS_TOKEN = os.getenv('SOURCE_INTERCOM_ACCESS_TOKEN')
TARGET_ACCESS_TOKEN = os.getenv('TARGET_INTERCOM_ACCESS_TOKEN')

def create_article(access_token, article_data):
    url = "https://api.intercom.io/articles"
    headers = {
        "Intercom-Version": "2.10",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=article_data)
    return response.json()

def export_articles_to_target(source_articles, target_access_token):
    for article in source_articles:
        # Prepare article data for creation in target organization
        article_data = {
            "title": article['title'],
            "description": article['description'],
            "body": article['body'],
            "author_id": article['author_id'],
            "state": article['state'],
            "parent_id": article['parent_id'],
            "parent_type": article['parent_type']
            
            # Add more fields if needed
        }

        # Create article in target organization
        response = create_article(target_access_token, article_data)
        if 'id' in response:
            print(f"Article '{article['title']}' created in target organization with ID: {response['id']}")
        else:
            print(f"Error creating article '{article['title']}' in target organization:", response)

if __name__ == "__main__":
    if SOURCE_ACCESS_TOKEN and TARGET_ACCESS_TOKEN:
        source_articles = articles_importer.get_all_articles(SOURCE_ACCESS_TOKEN)

        if source_articles:
            export_articles_to_target(source_articles, TARGET_ACCESS_TOKEN)
        else:
            print("Error fetching articles from source organization.")
    else:
        print("Source or target Intercom access token not found in .env file.")
