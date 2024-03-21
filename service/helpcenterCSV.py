import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SOURCE_ACCESS_TOKEN = os.getenv('SOURCE_INTERCOM_ACCESS_TOKEN')

def retrieve_help_center(access_token):
    url = "https://api.intercom.io/help_center/articles"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print(f"Error fetching help center articles: {response.json()}")
        return []

def export_to_csv(articles, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'title', 'body', 'author_id', 'state', 'created_at', 'updated_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow({
                'id': article.get('id', ''),
                'title': article.get('title', ''),
                'body': article.get('body', ''),
                'author_id': article.get('author_id', ''),
                'state': article.get('state', ''),
                'created_at': article.get('created_at', ''),
                'updated_at': article.get('updated_at', ''),
            })

if __name__ == "__main__":
    if SOURCE_ACCESS_TOKEN:
        help_center_articles = retrieve_help_center(SOURCE_ACCESS_TOKEN)

        if help_center_articles:
            export_to_csv(help_center_articles, 'help_center_articles.csv')
            print("Help center articles exported to help_center_articles.csv")
        else:
            print("No help center articles found.")
    else:
        print("Source Intercom access token not found in .env file.")
