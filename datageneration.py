import os
import time
import bisect
from faker import Faker

# File path to store the usernames
DATA_FILE = "usernames_2.txt"

# Number of usernames to generate
NUM_USERS = 5000000

### Generate and save usernames
def generate_usernames(num):
    """
    Generate 'num' unique usernames using Faker.
    To ensure uniqueness, a counter is appended to each generated username.
    Yields usernames one by one.
    """
    fake = Faker()
    for i in range(num):
        yield f"{fake.user_name()}_{i}"

def save_usernames(filename, num):
    """
    Generate 'num' unique usernames and save them to the specified file,
    one username per line.
    """
    print(f"Generating and saving {num} usernames to {filename}...")
    start = time.time()
    with open(filename, 'w', encoding='utf-8') as f:
        for username in generate_usernames(num):
            f.write(username + "\n")
    elapsed = time.time() - start
    print(f"Finished generating and saving usernames. Total time: {elapsed:.2f} seconds.")


for i in range(4):
    DATA_FILE = f'usernames_{i+1}M.txt'
    NUM_USERS = int(i+1) * 1000000
    if not os.path.exists(DATA_FILE):
        print(f"Data file {DATA_FILE} not found. Generating dataset...")
        save_usernames(DATA_FILE, NUM_USERS)