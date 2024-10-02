import requests
from bs4 import BeautifulSoup
import re
import csv
import utils

# get github repo links from html
def scrape_github_links(url):
    # Fetch the content of the README file
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links in the README
    links = soup.find_all("a", href=True)

    # Filter and collect GitHub repository links and names
    github_repos = []
    for link in links:
        href = link["href"]
        if re.match(r"https://github\.com/.+/.+", href):  # Check if it's a GitHub link
            repo_name = link.get_text(strip=True)  # Get the text (repository name)
            github_repos.append((repo_name, href))  # Store as a tuple (name, link)

    return github_repos


def save_links_to_csv(repos, filename="github_repos.csv"):
    # Save the links to a CSV file
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Repository Name", "GitHub Link", "Insert_Date"])  # Write header
        for name, link in repos:
            writer.writerow([name, link, utils.get_current_gmt9()])  # Write each name and link


if __name__ == "__main__":
    url = "https://github.com/jondot/awesome-react-native"
    github_repos = scrape_github_links(url)

    # Save the extracted links to a CSV file
    save_links_to_csv(github_repos)

    print(f"Saved {len(github_repos)} repositories to github_repos.csv")
