import csv
from datetime import datetime
import os
from pathlib import Path
from colorama import Fore, Style
from dotenv import load_dotenv
import requests
import utils
import glob

# Load environment variables from .env file
load_dotenv()

# Get the GitHub personal access token from the environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

input_suffix = 'contributors-202410041506'
input_file = Path.cwd() / f"res/{input_suffix}.csv"

version = utils.get_current_gmt9()
new_added = 0  # Initialize new_added globally
email_members = 0

def fetch_user_info(user):
    url = f"https://api.github.com/users/{user['username']}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        user_data = response.json()
        
        # Fetch email and check conditions
        fetched_email = user_data.get("email", "")
        
        # Use input user's email if fetched email is None or empty string
        if not fetched_email:
            fetched_email = user.get("email", "")
        
        # Check if the email is a noreply email
        if fetched_email and "noreply" in fetched_email:
            fetched_email = ""

        return {
            "username": user_data.get("login"),
            "name": user_data.get("name", ""),
            "email": fetched_email,
            "bio": user_data.get("bio", ""),
            "location": user_data.get("location", ""),
            "website": user_data.get("blog", ""),
            "followers": user_data.get("followers", 0),
            "repositories": user_data.get("public_repos", 0),
            "commit_date": user.get('commit_date', '')
        }
    elif response.status_code == 403:
        print(f"Access forbidden for {user['username']}: {response.json().get('message')}")
        return None
    else:
        print(f"Failed to fetch user info for {user['username']}: {response.status_code}")
        return None

def read_existing_usernames(prefix="users"):
    global email_members
    existing_usernames = set()
    
    # Construct the file pattern to match all files starting with the prefix in the res folder
    file_pattern = os.path.join("res", f"{prefix}*.csv")
    files = glob.glob(file_pattern)
    
    for filename in files:
        if os.path.isfile(filename):
            with open(filename, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_usernames.add(row["Username"])  # Collect existing usernames
                    if row["Email"]:
                        email_members += 1
                    
    return existing_usernames

existing_usernames = []  # Read existing usernames

def save_user_info_to_csv(user_info_list, filename=f"res/users-{version}.csv"):
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
                    "UserLink",
                    "Commit_Date"
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
                        f"https://github.com/{user_info['username']}",  # Fixed the syntax error here
                        user_info['commit_date']
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
        reader = csv.DictReader(file)  # Use DictReader for easier access by column names
        contributors = []  # Use a list to store contributors
        
        for row in reader:
            contributor = {
                "username": row['User Link'],
                "email": row["Email"],
                "commit_date": row.get("Commit Date")  # Use .get() to avoid KeyError if the column doesn't exist
            }
            contributors.append(contributor)  # Store contributor as a dictionary

    global existing_usernames
    existing_usernames = read_existing_usernames()

    user_info_list = []  # Initialize an empty list to store user info
    length = len(contributors)

    for index, user in enumerate(contributors):
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
        f"Imported Members:   {new_added}/{length}\n"  # Fixed here to use length of contributors
        f"Result Members:     {len(existing_usernames)}\n"
        f"Email Members:      {email_members}\n"
        f"{'-' * 35}"
    )

if __name__ == "__main__":
    main()
