import csv
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import utils

# Load environment variables from .env file
load_dotenv()

version = utils.get_current_gmt9()

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
            search_url = f"{url}?{urlencode(params)}"
            print(search_url)
            data = response.json()
            repositories.extend(data["items"])
            # print(f"({page} page) {repositories}")
            if (
                len(data["items"]) < per_page
            ):  # If fewer than per_page items returned, we're done
                break
            page += 1  # Go to the next page
            save_repositories_to_csv(data["items"], search_url)
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break

    return repositories


import csv
from pathlib import Path


def save_repositories_to_csv(
    repositories, search_url, filename=f"res/repositories-{version}.csv"
):
    Path("res").mkdir(parents=True, exist_ok=True)

    # Read existing URLs from the CSV file
    existing_urls = set()
    write_header = not Path(filename).exists() or Path(filename).stat().st_size == 0

    if Path(filename).exists():
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Use DictReader to access by header name
            existing_urls = {row["html_url"] for row in reader}  # Collect existing URLs

    # Write new entries to the CSV
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header if the file is empty
        if write_header:
            writer.writerow(
                [
                    "full_name",
                    "html_url",
                    "search_url",
                    "created_at",
                    "updated_at",
                    "repo_language",
                    "star",
                    "forks",
                    "open_issues",
                ]
            )

        for repo in repositories:
            repo_url = repo["html_url"]
            if repo_url not in existing_urls:  # Only add if URL is unique
                writer.writerow(
                    [
                        repo["full_name"],
                        repo_url,
                        search_url,
                        repo["created_at"],
                        repo["updated_at"],
                        repo["language"],
                        repo["stargazers_count"],
                        repo["forks"],
                        repo["open_issues"],
                    ]
                )
                existing_urls.add(repo_url)  # Update the set of existing URLs


def main():
    blockchain_keywords = [
        "Tokenization",
        "Distributed Ledger",
        "Fork",
        "Mining",
        "Ledger",
        "Public Blockchain",
        "Private Blockchain",
        "DApp (Decentralized Application)",
        "Gas Fees",
        "Interoperability",
        "Tokenomics",
        "ICO (Initial Coin Offering)",
        "DAO (Decentralized Autonomous Organization)",
        "Validator",
        "Supply Chain Management",
        "Immutable",
        "Address",
        "Sidechain",
        "Sharding",
    ]

    for q in blockchain_keywords:
        result = search_repositories(q)


if __name__ == "__main__":
    main()
