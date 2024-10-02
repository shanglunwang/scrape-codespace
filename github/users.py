import csv
from datetime import datetime
import os
from pathlib import Path
from colorama import Fore, Style
from dotenv import load_dotenv
import requests
import utils

# Load environment variables from .env file
load_dotenv()

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

input_suffix = 'contributors-202410021911'
input_file = Path.cwd() / "contributors.csv"

version = utils.get_current_gmt9()
user_input_file = Path.cwd() / f"res/{input_suffix}.csv"
new_added = 0  # Initialize new_added globally
email_members = 0


def fetch_user_info(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        user_data = response.json()
        return {
            "username": user_data.get("login"),
            "name": user_data.get("name", ""),
            "email": user_data.get("email", ""),
            "bio": user_data.get("bio", ""),
            "location": user_data.get("location", ""),
            "website": user_data.get("blog", ""),
            "followers": user_data.get("followers", 0),
            "repositories": user_data.get("public_repos", 0),
        }
    elif response.status_code == 403:
        print(f"Access forbidden for {username}: {response.json().get('message')}")
        return None
    else:
        print(f"Failed to fetch user info for {username}: {response.status_code}")
        return None


def read_existing_usernames(filename):
    global email_members
    existing_usernames = set()
    if os.path.isfile(filename):
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_usernames.add(row["Username"])  # Collect existing usernames
                if row["Email"]:
                    email_members += 1
    return existing_usernames


existing_usernames = []  # Read existing usernames[p]


def save_user_info_to_csv(user_info_list, filename=f"users-{version}.csv"):
    global new_added  # Declare new_added as global
    global existing_usernames
    global email_members

    file_exists = os.path.isfile(filename)  # Check if the file already exists

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header only if the file does not exist
            writer.writerow(
                [
                    "Username",
                    "Name",
                    "Email",
                    "Bio",
                    "Location",
                    "Website",
                    "Followers",
                    "Repositories",
                    "Insert_Date",
                    "UserLink"
                ]
            )  # Header
        for user_info in user_info_list:
            if user_info["username"] not in existing_usernames:  # Check for duplicates
                writer.writerow(
                    [
                        user_info["username"],
                        user_info["name"],
                        user_info["email"],
                        user_info["bio"],
                        user_info["location"],
                        user_info["website"],
                        user_info["followers"],
                        user_info["repositories"],
                        utils.get_current_gmt9(),
                        f"https://github.com/{user_info["username"]}"
                    ]
                )
                existing_usernames.add(
                    user_info["username"]
                )  # Update the set with new username

                if user_info["email"]:
                    email_members += 1
                new_added += 1  # Increment new_added


def main():
    with open(input_file, mode="r", newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        usernames = [row[1] for row in reader]  # Ensure correct index for usernames

    global existing_usernames
    existing_usernames = read_existing_usernames(user_input_file)

    user_info_list = []  # Initialize an empty list to store user info
    length = len(usernames)

    for index, user in enumerate(usernames):
        user_info = fetch_user_info(user)
        if user_info:
            user_info_list.append(user_info)  # Append only the user info
            if user_info["username"] not in existing_usernames:  # Check for duplicates
                # Print the index and user information
                print(f"• {index + 1}/{length} | New Inserted | {user_info}")
            else:
                print(f"• {index + 1}/{length} | Existed | {user_info}")

            save_user_info_to_csv([user_info])

    print(
        f"{Fore.GREEN}🎉 Import Finished! 🎉{Style.RESET_ALL}\n"
        f"{'-' * 35}\n"
        f"Imported Members:   {new_added}/{len(usernames)}\n"
        f"Result Members:     {len(existing_usernames)}\n"
        f"Email Members:      {email_members}\n"
        f"{'-' * 35}"
    )


if __name__ == "__main__":
    main()
