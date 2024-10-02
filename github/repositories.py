import csv
import os
from pathlib import Path
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def search_repositories(query, sort="updated", order="desc"):
    url = "https://api.github.com/search/repositories"
    repositories = []
    page = 1
    per_page = 100  # Maximum per page

    while True:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }

        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            repositories.extend(data["items"])
            print(repositories)
            if (
                len(data["items"]) < per_page
            ):  # If fewer than per_page items returned, we're done
                break
            page += 1  # Go to the next page
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break

    return repositories


def save_repositories_to_csv(repositories, filename="repositories.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Repo Name", "URL"])  # Header
        for repo in repositories:
            writer.writerow([repo["full_name"], repo["html_url"]])

def main():
    query = "smart contract"
    result = search_repositories(query)
    save_repositories_to_csv(result)


if __name__ == "__main__":
    main()
