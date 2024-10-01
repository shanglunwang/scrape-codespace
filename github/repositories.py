import csv
import os
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

# Specify the path to your CSV file
file_path = "path/to/your/file.csv"

# Read the CSV file
with open(file_path, mode="r", newline="") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    repo_names = [row[0] for row in reader]  # Extract repository names

# Print the repository names
print(repo_names)
def main():
    query = "solana stars:>1"
    result = search_repositories(query)
    save_repositories_to_csv(result)


if __name__ == "__main__":
    main()
