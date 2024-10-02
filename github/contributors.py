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

    while page <= 5:
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
                        contributor = commit["author"]["login"]
                        contributors.add(contributor)
            page += 1  # Go to the next page
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return []

    return list(contributors)


def save_user_links_to_csv(repo_user_links, filename="contributors.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "User Link"])  # Header
        for repo, link in repo_user_links:
            writer.writerow([repo, link])


def main():
    with open(input_file, mode="r", newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        repo_names = [row[0] for row in reader]  # Extract repository names

    repo_user_links = []  # List to hold tuples of (repo, user link)

    for index, repo in enumerate(repo_names):
        new_links = fetch_recent_contributors(repo)  # Get recent contributors
        print(
            f"• {index}/{len(repo_names)} | {repo}: {new_links}"
        )  # Print the index along with the repo and contributors

        # Add repo-user link tuples to the list
        for user in new_links:
            repo_user_links.append((repo, user))
            # Save user links to CSV if the list is not empty
            if repo_user_links:
                save_user_links_to_csv(repo_user_links)

    # Save to CSV


if __name__ == "__main__":
    main()
