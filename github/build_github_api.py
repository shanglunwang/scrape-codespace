import pandas as pd
import sqlite3
from pathlib import Path
import requests
import os
from dotenv import load_dotenv

directory = Path.cwd()

file_paths = [f for f in directory.iterdir() if f.is_file()]
file_paths = [directory / "contributors.xlsx"]


conn = sqlite3.connect("users.db")
cursor = conn.cursor()

new_github = []
for file_path in file_paths:
    # df = pd.read_excel(file_path, engine="openpyxl")
    print(file_path)
    df = pd.read_excel(file_path)
    for index, row in df.iterrows():
        new_github.append(row.get("UserLink-href"))

cursor.execute("""SELECT github FROM tb_users_github""")
rows = cursor.fetchall()
db_github = []
for row in rows:
    db_github.append(row[0])

common = set(db_github) & set(new_github)
new_github = [item for item in new_github if item not in db_github]

usernames = []
for item in new_github:
    usernames.append(item.replace("https://github.com/", ""))


url = "https://api.github.com/graphql"
# Load environment variables from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    print("Error: GITHUB_TOKEN is not set.")
    exit(1)

token = GITHUB_TOKEN

# Set headers
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def split_list(lst, chunk_size):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


chunks = split_list(usernames, 1000)

results = []
for unit in chunks:
    query = "{\n"
    for i, username in enumerate(unit):
        query += f'  user{i + 1}: user(login: "{username}") {{\n'
        query += "    email\n"
        query += "    name\n"
        query += "    login\n"
        query += "    location\n"
        query += "  }\n"
    query += "}"

    # print(query)

    # Make the request
    response = requests.post(url, json={"query": query}, headers=headers)

    # Print the response
    if response.status_code == 200:
        data = response.json()

        for user_key, user_info in data["data"].items():
            if user_info is None:
                continue
            email = user_info["email"]
            name = user_info["name"]
            login = user_info["login"]
            location = user_info["location"]
            if email == "":
                continue
            else:
                results.append((name, location, email, "https://github.com/" + login))
            print(
                f"User: {user_key}, Name: {name}, Email: {email}, Login: {login}, Location: {location}"
            )
    else:
        print("Error:", response.status_code, response.text)

    # break
print(len(results))
cursor.executemany(
    """INSERT INTO tb_users_github(name, location, email, github) VALUES (?, ?, ?, ?)""",
    results,
)
conn.commit()

conn.close()
