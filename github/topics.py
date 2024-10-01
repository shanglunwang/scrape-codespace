# not compeleted
import requests
from bs4 import BeautifulSoup
import csv


def scrape_github_topics():
    url = "https://github.com/topics"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        topics = []

        # Find all topic elements
        for topic in soup.find_all("div", class_="topic-box"):
            h3 = topic.h3
            if h3 and h3.a:  # Check if h3 and h3.a exist
                name = h3.a.text.strip()
                link = "https://github.com" + h3.a["href"]

                # Get the description if available
                description = topic.p.text.strip() if topic.p else "No description"

                topics.append({"name": name, "description": description, "link": link})

        return topics
    else:
        print(f"Failed to fetch topics: {response.status_code}")
        return []


def save_to_csv(data, filename="github_topics.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Description", "Link"])  # Header
        for topic in data:
            writer.writerow([topic["name"], topic["description"], topic["link"]])


def main():
    topics = scrape_github_topics()
    if topics:
        save_to_csv(topics)
        print(f"GitHub topics saved to github_topics.csv")


if __name__ == "__main__":
    main()
