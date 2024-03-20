import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')

def get_all_articles(access_token):
    url = "https://api.intercom.io/articles"
    headers = {
        "Intercom-Version": "2.10",
        "Authorization": f"Bearer {access_token}"
    }
    all_articles = []

    # Initial GET request
    response = requests.get(url, headers=headers)
    data = response.json()

    # Check for valid response and extract articles
    if 'data' in data:
        all_articles.extend(data['data'])
    else:
        print("Error fetching articles:", data)

    # Check if there are more pages of articles
    while 'pages' in data and 'next' in data['pages']:
        next_page_url = data['pages']['next']
        response = requests.get(next_page_url, headers=headers)
        data = response.json()

        # Check for valid response and extract articles
        if 'data' in data:
            all_articles.extend(data['data'])
        else:
            print("Error fetching articles:", data)

    return all_articles

def export_to_csv(articles, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=articles[0].keys())
        writer.writeheader()
        writer.writerows(articles)

if __name__ == "__main__":
    if ACCESS_TOKEN:
        all_articles = get_all_articles(ACCESS_TOKEN)

        if all_articles:
            export_to_csv(all_articles, 'intercom_articles.csv')
            print("Articles exported to intercom_articles.csv")
        else:
            print("Error fetching articles.")
    else:
        print("Intercom access token not found in .env file.")
