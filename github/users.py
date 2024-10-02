import csv
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import utils

# Load environment variables from .env file
load_dotenv()

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

input_file = Path.cwd() / "contributors.csv"
user_input_file = Path.cwd() / "users.csv"
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


existing_usernames = read_existing_usernames(user_input_file)  # Read existing usernames


def save_user_info_to_csv(user_info_list, filename="user_info.csv"):
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

    user_info_list = []  # Initialize an empty list to store user info
    length = len(usernames)
    for index, user in enumerate(usernames):
        user_info = fetch_user_info(user)
        if user_info:
            user_info_list.append(user_info)  # Append only the user info
            if user_info["username"] not in existing_usernames:  # Check for duplicates
                # Print the index and user information
                print(f"({index}/{length}) New Inserted: {user_info}")
            else:
                print(f"({index}/{length}) Already Existed: {user_info}")
            save_user_info_to_csv([user_info])

    print(
        f"Import Finished. Imported_Members: {new_added}/{len(usernames)}, Result_Members: {len(existing_usernames)}, Email_Members: {email_members}"
    )


if __name__ == "__main__":
    main()
