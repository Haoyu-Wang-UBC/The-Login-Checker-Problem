import time
import pickle
from bloomfilter import BloomFilter
from cuckoofilter import CuckooFilter

# DATA_FILE = "usernames_2.txt"
# BLOOM_FILTER_FILE = "bloom_filter_2.pkl"
# CUCKOO_FILTER_FILE = "cuckoo_filter_2.pkl"
CHUNK_SIZE = 5_000_000

def load_usernames(filename):
    """
    Load usernames from the specified file (one per line) and return them as a list.
    """
    print(f"Loading usernames from file {filename}...")
    start = time.time()
    usernames = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            usernames.append(line.strip())
    elapsed = time.time() - start
    print(f"Loaded {len(usernames)} usernames in {elapsed:.2f} seconds.")
    return usernames

def initialize_filters(DATA_FILE, BLOOM_FILTER_FILE, CUCKOO_FILTER_FILE):
    """Initialize BloomFilter & CuckooFilter, and store them efficiently."""
    print("\n[Initializing Filters...]")

    usernames = load_usernames(DATA_FILE)

    bloom_filter = BloomFilter(items_count=len(usernames), fp_prob=0.01)
    cuckoo_filter = CuckooFilter(capacity=len(usernames))

    start = time.time()
    chunk_counter = 0

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        while True:
            chunk = [f.readline().strip() for _ in range(CHUNK_SIZE)]
            if not chunk[0]:
                break

            for username in chunk:
                bloom_filter.add(username)
                cuckoo_filter.insert(username)

            chunk_counter += 1
            print(f"Processed chunk {chunk_counter}...")

    time_insert = time.time() - start
    print(f"Insert time : {time_insert:.2f} seconds.")

    print(f"The load factor is:{cuckoo_filter.load_factor():.2%}")

    # Chunked Storage in Bloom Filter
    with open(BLOOM_FILTER_FILE, "wb") as bf_file:
        for i in range(0, len(bloom_filter.bit_array), CHUNK_SIZE):
            chunk = bloom_filter.bit_array[i:i + CHUNK_SIZE]
            pickle.dump(chunk, bf_file)
            print(f"Saved BloomFilter chunk {i // CHUNK_SIZE + 1}")

    # Chunked Storage in Cuckoo Filter
    with open(CUCKOO_FILTER_FILE, "wb") as cf_file:
        for i in range(0, len(cuckoo_filter.buckets), CHUNK_SIZE):
            chunk = cuckoo_filter.buckets[i:i + CHUNK_SIZE]
            pickle.dump(chunk, cf_file)
            print(f"Saved CuckooFilter chunk {i // CHUNK_SIZE + 1}")

    print("Filters saved efficiently!")

if __name__ == "__main__":
    for i in range(4):
        DATA_FILE = f"usernames_{i+1}M.txt"
        BLOOM_FILTER_FILE = f"bloom_filter_{i+1}M.pkl"
        CUCKOO_FILTER_FILE = f"cuckoo_filter_{i+1}M.pkl"
        initialize_filters(DATA_FILE, BLOOM_FILTER_FILE, CUCKOO_FILTER_FILE)
