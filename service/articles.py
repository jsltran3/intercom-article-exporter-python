import requests
import csv

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
    all_articles.extend(data['data'])

    # Check if there are more pages of articles
    while 'next' in data['pages']:
        next_page_url = data['pages']['next']
        response = requests.get(next_page_url, headers=headers)
        data = response.json()
        all_articles.extend(data['data'])

    return all_articles

def export_to_csv(articles, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=articles[0].keys())
        writer.writeheader()
        writer.writerows(articles)

if __name__ == "__main__":
    # Replace 'YOUR_TOKEN_HERE' with your actual Intercom access token
    access_token = "TOKEN HERE"
    all_articles = get_all_articles(access_token)

    # Export articles to CSV file
    export_to_csv(all_articles, 'intercom_articles.csv')
    print("Articles exported to intercom_articles.csv")
