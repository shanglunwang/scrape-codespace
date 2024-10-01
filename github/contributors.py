from pathlib import Path
import requests
from dotenv import load_dotenv
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

input_file = Path.cwd() / "repositories.csv"

# Load environment variables from .env file
load_dotenv()

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def fetch_most_contributors(repo):
    # Construct the API URL for contributors
    url = f"https://api.github.com/repos/{repo}/contributors"
    response = requests.get(url)

    if response.status_code == 200:
        contributors = response.json()
        user_links = [contributor["html_url"] for contributor in contributors]
        return user_links
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []


def fetch_recent_contributors(repo):
    # Calculate the date 30 days ago from today
    days_ago = datetime.now() - timedelta(days=30)

    contributors = set()
    page = 1

    while page <= 1:
        # Construct the API URL for commits with pagination
        url = f"https://api.github.com/repos/{repo}/commits?page={page}"
        response = requests.get(url, headers=HEADERS)  # Add headers for authentication

        if response.status_code == 200:
            commits = response.json()

            if not commits:  # Break the loop if no more commits are returned
                break

            # Collect contributors who have committed in the last 30 days
            for commit in commits:
                commit_date = datetime.strptime(
                    commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"
                )
                if commit_date >= days_ago:
                    # Check if the author exists
                    if commit.get("author") and commit["author"].get("login"):
                        contributors.add(commit["author"]["login"])

            page += 1  # Go to the next page
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return []

    return list(contributors)


def save_user_links_to_csv(user_links, filename="contributors.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["User Link"])  # Header
        for link in user_links:
            writer.writerow([link])


def main():
    with open(input_file, mode="r", newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        repo_names = [row[0] for row in reader]  # Extract repository names

    userlinks = []

    for repo in repo_names:
        new_links = fetch_recent_contributors(repo)  # Pass the repo object
        userlinks.extend(new_links)  # Add new links to the existing userlinks array
        if userlinks:
            save_user_links_to_csv(userlinks)  # Save to CSV


if __name__ == "__main__":
    main()
