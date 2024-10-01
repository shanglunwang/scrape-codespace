import os
import requests
import csv

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def search_github_topics(query):
    url = f"https://api.github.com/search/topics?q={query}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch topics: {response.status_code}")
        return None


def save_to_csv(data, filename="github_topics.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Description"])  # Header
        for topic in data["items"]:
            writer.writerow([topic["name"], topic["description"]])


def main():
    query = "python"  # Change this to the topic you want to search
    topics = search_github_topics(query)

    if topics:
        save_to_csv(topics)
        print(f"Topic information matching '{query}' saved to github_topics.csv")


if __name__ == "__main__":
    main()
