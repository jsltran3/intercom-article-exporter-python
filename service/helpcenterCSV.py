import os
import csv
import requests
from time import sleep
from dotenv import load_dotenv
import logging
import html

load_dotenv()
SRC_INTERCOM_ACCESS_TOKEN = os.getenv('DOCKETWISE_SRC_ACCESS_TOKEN')
DEST_INTERCOM_ACCESS_TOKEN = os.getenv('AFFINIPAY_DEST_TEST_ACCESS_TOKEN')
DEST_AUTHOR_ID = os.getenv('AFFINIPAY_DEST_TEST_AUTHOR_ID')

class HelpCenterMigrator:
    def __init__(self, src_access_token, dest_access_token, dest_article_auth_id):
        self.src_access_token = src_access_token
        self.dest_access_token = dest_access_token
        self.dest_article_auth_id = dest_article_auth_id

        self.get_src_help_centers_response, self.all_src_help_centers = self.get_all_help_centers(src_access_token)
        self.get_dest_help_centers_response, self.all_dest_help_centers = self.get_all_help_centers(dest_access_token)
        self.get_src_articles_response, self.all_src_articles = self.get_all_articles(src_access_token)
        self.get_dest_articles_response, self.all_dest_articles = self.get_all_articles(dest_access_token)

    def duplicate_all_help_centers(self):
        if (self.get_src_help_centers_response.status_code == 200 and
            self.get_dest_help_centers_response.status_code == 200
        ):
            for src_help_center in self.all_src_help_centers:
                self.duplicate_help_center_in_dest(src_help_center)

    def duplicate_help_center_in_dest(self, src_help_center):
        if (self.get_src_help_centers_response.status_code == 200 and
            self.get_dest_help_centers_response.status_code == 200 and
            src_help_center['display_name'] != None
        ):
            print(f"{src_help_center['display_name']}:")

            # Skip copying if the same help center doesn't exist in the destination
            dest_help_center = self.get_matching_dest_help_center(src_help_center['display_name'])
            if not dest_help_center:
                print(f"\t- '{src_help_center['display_name']}' not found on the destination Intercom workspace. Please manually create this Help Center.")
                return
            else:
                print(f"\t- Matching help center {src_help_center['display_name']} found in destination Intercom workspace.")
                self.get_dest_collections_response, self.all_dest_collections = self.get_all_collections(self.dest_access_token, dest_help_center['id'])

            # Recreate top-level collection structure in destination
            self.get_src_collections_response, self.all_src_collections = self.get_all_collections(self.src_access_token, src_help_center['id'])
            src_top_level_collections = [collection for collection in self.all_src_collections if collection['help_center_id'] == int(src_help_center['id']) and collection['parent_id'] == None]
            print("\t- Recreating collection structure in destination Intercom workspace.")
            for src_top_level_collection in src_top_level_collections:
                self.recreate_all_collections_in_dest(dest_help_center, None, src_top_level_collection, tabs_to_print=2)

            # Re-index all destination collections, then recreate all articles in dest
            self.get_dest_collections_response, self.all_dest_collections = self.get_all_collections(self.dest_access_token, dest_help_center['id'], pre_sleep=10)
            print("\t- Recreating articles in destination Intercom workspace.")
            for src_top_level_collection in src_top_level_collections:
                self.recreate_all_articles_in_dest(dest_help_center, None, src_top_level_collection, tabs_to_print=2)
            print("\n")

            # Re-index all destination collections, then update all collections in the dest to respect the correct icons
            self.get_dest_collections_response, self.all_dest_collections = self.get_all_collections(self.dest_access_token, dest_help_center['id'], pre_sleep=10)
            print("\t- Updating collection icons in destination to match source collections.")
            for src_top_level_collection in src_top_level_collections:
                self.update_all_collection_icons_in_dest(dest_help_center, None, src_top_level_collection, tabs_to_print=2)
            return []
        
        if self.get_src_help_centers_response.status_code != 200 :
            print(f"Error fetching source help centers: {self.get_src_help_centers_response.status_code} - {self.get_src_help_centers_response.json()}")
        if self.get_dest_help_centers_response.status_code != 200:
            print(f"Error fetching destination help centers: {self.get_dest_help_centers_response.status_code} - {self.get_dest_help_centers_response.json()}")
        return []

    def get_all_help_centers(self, access_token):
        url = "https://api.intercom.io/help_center/help_centers"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Intercom-Version": "2.10",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        help_centers = response.json().get('data', [])

        return response, help_centers

    def get_all_collections(self, access_token, help_center_id, pre_sleep=0):
        if pre_sleep:
            sleep(pre_sleep)

        all_data = []
        page = 1
        total_pages = 1  # Start with 1 to enter the loop
        params = {'page': page}

        url = f"https://api.intercom.io/help_center/collections?help_center_id={help_center_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Intercom-Version": "2.10",
            "Accept": "application/json"
        }

        while page <= total_pages:
            params['page'] = page
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                all_data.extend(data['data'])
                total_pages = data['pages']['total_pages']
                page += 1
            else:
                print(f"Error: {response.status_code}")
                break

        return response, all_data
    
    def get_all_articles(self, access_token):
        all_data = []
        page = 1
        total_pages = 1  # Start with 1 to enter the loop
        params = {'page': page}

        url = "https://api.intercom.io/articles"
        headers = {
            "Intercom-Version": "2.10",
            "Authorization": f"Bearer {access_token}"
        }

        while page <= total_pages:
            params['page'] = page
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                all_data.extend(data['data'])
                total_pages = data['pages']['total_pages']
                page += 1
            else:
                print(f"Error: {response.status_code}")
                break

        return response, all_data

    def get_matching_dest_help_center(self, src_help_center_name):
        """Returns the destination help center object with the matching help center name"""
        for help_center in self.all_dest_help_centers:
            if help_center['display_name'] == src_help_center_name:
                return help_center
        return None

    def get_matching_dest_collection(self, dest_help_center_id, dest_parent_id, src_collection_name):
        """Returns the destination collection object with the matching collection name"""
        for dest_collection in self.all_dest_collections:
            if (dest_collection['help_center_id'] == int(dest_help_center_id) and 
                dest_collection['parent_id'] == dest_parent_id and
                dest_collection['name'] == (src_collection_name)
            ):
                return dest_collection
        return None

    def recreate_all_collections_in_dest(self, dest_help_center, dest_parent_id, src_curr_collection, tabs_to_print):
        """Recreates the collection structure in the destination Intercom workspace.
        If the 'dest_parent_id' is defined, this method will create a nested collection underneath the collection with 'parent_id'
        """
        tabs_str = '\t' * tabs_to_print
        # Check if the collection name is already decoded
        unescaped_name = src_curr_collection['name']
        if "&" in unescaped_name and not any(entity in unescaped_name for entity in ["&amp;", "&lt;", "&gt;", "&quot;", "&#39;"]):
            unescaped_name = html.unescape(unescaped_name)

        # 1. Fetch matching destination collection or create one if it doesn't exist
        dest_collection = self.get_matching_dest_collection(dest_help_center['id'], dest_parent_id, unescaped_name)

        if not dest_collection:
            print(f"{tabs_str}- Source collection '{html.unescape(src_curr_collection['name'])}' not found under parent destination collection.")
            dest_collection = self.create_collection_copy_in_dest(dest_help_center['id'], dest_parent_id, src_curr_collection, tabs_to_print+1)
            if not dest_collection:
                return
        else:
            print(f"{tabs_str}- Matching collection '{html.unescape(src_curr_collection['name'])}' found in destination Intercom workspace.")
        dest_parent_id = dest_collection['id']

        # 2. At the current src_collection, check if there are any collections whos parent_id is the current top_level collection
        src_nested_collections = [collection for collection in self.all_src_collections if collection['parent_id'] == src_curr_collection['id']]

        # 3. Recursively create sub-directories
        for collection in src_nested_collections:
            self.recreate_all_collections_in_dest(dest_help_center, dest_collection['id'], collection, tabs_to_print+1)

    def recreate_all_articles_in_dest(self, dest_help_center, dest_parent_collection_id, src_curr_collection, tabs_to_print):
        # 1. Fetch matching destination collection
        collections_tabs_str = '\t' * tabs_to_print
        dest_collection = self.get_matching_dest_collection(dest_help_center['id'], dest_parent_collection_id, src_curr_collection['name'])

        if not dest_collection:
            print(f"{collections_tabs_str}- Source collection '{html.unescape(src_curr_collection['name'])}' not found under parent destination collection.")
            print(f"{collections_tabs_str}\t- Will not create copy of articles since parent container is missing.")
            return
        else:
            print(f"{collections_tabs_str}- Matching collection '{html.unescape(src_curr_collection['name'])}' found in destination Intercom workspace.")
        dest_parent_collection_id = dest_collection['id']

        # 2. Copy articles into this same level directory
        articles_tab_str = '\t' * (tabs_to_print + 1)
        dest_articles = [article for article in self.all_dest_articles if article['parent_id'] == int(dest_parent_collection_id)]
        dest_article_titles = [html.unescape(article['title']) for article in dest_articles]
        src_articles = [article for article in self.all_src_articles if article['parent_id'] == int(src_curr_collection['id'])]

        for src_article in src_articles:
            # Skip if the article already exists
            if html.unescape(src_article['title']) in dest_article_titles:
                print(f"{articles_tab_str}- Matching article '{html.unescape(src_article['title'])}' found in current destination directory. Will not make another copy.")
                continue
            else:
                self.create_article_copy_in_dest(dest_parent_collection_id, src_article, tabs_to_print+1)
        
        # 3. Recurse into sub-directory
        src_nested_collections = [collection for collection in self.all_src_collections if collection['parent_id'] == src_curr_collection['id']]

        for src_collection in src_nested_collections:
            self.recreate_all_articles_in_dest(dest_help_center, dest_parent_collection_id, src_collection, tabs_to_print+1)

    def update_all_collection_icons_in_dest(self, dest_help_center, dest_parent_collection_id, src_curr_collection, tabs_to_print):
        """Updates the collection structure in the destination Intercom workspace.
        If the 'dest_parent_id' is defined, this method will create a nested collection underneath the collection with 'parent_id'
        """
        tabs_str = '\t' * tabs_to_print
        # Check if the collection name is already decoded
        unescaped_name = src_curr_collection['name']
        if "&" in unescaped_name and not any(entity in unescaped_name for entity in ["&amp;", "&lt;", "&gt;", "&quot;", "&#39;"]):
            unescaped_name = html.unescape(unescaped_name)

        # 1. Fetch matching destination collection
        dest_collection = self.get_matching_dest_collection(dest_help_center['id'], dest_parent_collection_id, unescaped_name)

        if not dest_collection:
            print(f"{tabs_str}- Source collection '{html.unescape(src_curr_collection['name'])}' not found under parent destination collection.")
            if not dest_collection:
                return
        else:
            print(f"{tabs_str}- Matching collection '{html.unescape(src_curr_collection['name'])}' found in destination Intercom workspace. Updating icons to match.")
            self.update_dest_icon_to_source(dest_collection, src_curr_collection, tabs_to_print+1)

        dest_parent_collection_id = dest_collection['id']

        # 2. At the current src_collection, check if there are any collections whos parent_id is the current top_level collection
        src_nested_collections = [collection for collection in self.all_src_collections if collection['parent_id'] == src_curr_collection['id']]

        # 3. Recursively create sub-directories
        for collection in src_nested_collections:
            self.update_all_collection_icons_in_dest(dest_help_center, dest_collection['id'], collection, tabs_to_print+1)

    def update_dest_icon_to_source(self, dest_collection, src_collection, tabs_to_print):
        url = f"https://api.intercom.io/help_center/collections/{dest_collection['id']}"
        payload = {
            "icon": src_collection['icon']
        }
        headers = {
            "Content-Type": "application/json",
            "Intercom-Version": "2.10",
            "Authorization": f"Bearer {self.dest_access_token}",
            "Accept": "application/json"
        }

        response = requests.put(url, json=payload, headers=headers)
        request_id = response.headers.get('X-Request-Id')
        tabs_str = '\t' * tabs_to_print

        if response.status_code == 200:
            print(f"{tabs_str}- Collection was updated successfully.")
            print(f"{tabs_str}- Request ID: {request_id}")
            return response.json()
        else:
            print(f"{tabs_str}- Error updating collection: {response.status_code} - {response.json()}")
            print(f"{tabs_str}- Request ID: {request_id}")

    def create_collection_copy_in_dest(self, dest_help_center_id, dest_parent_id, src_collection, tabs_to_print):
        """Creates a collection in the destination Intercom workspace with the same name and structure of the source collection."""
        url = "https://api.intercom.io/help_center/collections"
        unescaped_name = html.unescape(src_collection['name'])

        payload = {
            "name": unescaped_name,
            "description": src_collection["description"],
            "parent_id": dest_parent_id,
            "help_center_id": dest_help_center_id,
            "icon": src_collection["icon"],
            "order": src_collection["order"]
        }
        headers = {
            "Content-Type": "application/json",
            "Intercom-Version": "2.10",
            "Authorization": f"Bearer {self.dest_access_token}",
        }

        response = requests.post(url, json=payload, headers=headers)
        request_id = response.headers.get('X-Request-Id')
        tabs_str = '\t' * tabs_to_print

        if response.status_code == 200:
            print(f"{tabs_str}- Copy of collection created successfully.")
            print(f"{tabs_str}- Request ID: {request_id}")
            return response.json()
        else:
            print(f"{tabs_str}- Error creating copy of collection: {response.status_code} - {response.json()}")
            print(f"{tabs_str}- Request ID: {request_id}")

    def create_article_copy_in_dest(self, dest_parent_id, src_article, tabs_to_print) -> None:
        """Creates an article in the destination Intercom workspace with the same content of the source article."""
        url = "https://api.intercom.io/articles"

        # Check if the article title is already decoded
        unescaped_title = src_article["title"]
        if "&" in unescaped_title and not any(entity in unescaped_title for entity in ["&amp;", "&lt;", "&gt;", "&quot;", "&#39;"]):
            unescaped_title = html.unescape(unescaped_title)

        payload = {
            "title": unescaped_title,
            "description": src_article["description"],
            "body": src_article["body"],
            "author_id": self.dest_article_auth_id,
            "state": src_article["state"],
            "parent_id": dest_parent_id,
            "parent_type": src_article["parent_type"]
        }
        headers = {
            "Content-Type": "application/json",
            "Intercom-Version": "2.10",
            "Authorization": f"Bearer {self.dest_access_token}"
        }

        response = requests.post(url, json=payload, headers=headers)
        request_id = response.headers.get('X-Request-Id')
        tabs_str = '\t' * tabs_to_print
        
        if response.status_code == 200:
            created_article = response.json()
            print(f"{tabs_str}- Copy of article '{created_article['title']}' created successfully.")
            print(f"{tabs_str}- Request ID: {request_id}")
            return created_article
        else:
            print(f"{tabs_str}- Error creating copy of article: {response.status_code} - {response.json()}")
            print(f"{tabs_str}- Request ID: {request_id}")

    def export_to_csv(self, data, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

if __name__ == "__main__":
    migrator = HelpCenterMigrator(SRC_INTERCOM_ACCESS_TOKEN, DEST_INTERCOM_ACCESS_TOKEN, DEST_AUTHOR_ID)

    if SRC_INTERCOM_ACCESS_TOKEN and DEST_INTERCOM_ACCESS_TOKEN:
        migrator.duplicate_all_help_centers()