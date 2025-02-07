import os
import time
import bisect
from faker import Faker
from bloomfilter import BloomFilter
from cuckoofilter import CuckooFilter
from random import shuffle
import unittest
import pickle
from bitarray import bitarray

# File path
iii = 5 # number of users you want to use, in 'million'
# DATA_FILE = "usernames_2.txt"
# sorted_data_path = "sorted_usernames_2.txt"
# # set_data_path = "usernames_set_2.pkl"
# BLOOM_FILTER_FILE = "bloom_filter_2.pkl"
# CUCKOO_FILTER_FILE = "cuckoo_filter_2.pkl"

DATA_FILE = f"usernames_5M.txt"
# sorted_data_path = f"sorted_usernames_{iii}M.txt"
BLOOM_FILTER_FILE = f"bloom_filter_2.pkl"
CUCKOO_FILTER_FILE = f"cuckoo_filter_2.pkl"

def load_usernames(filename, max_users):
    """
    Load usernames from the specified file (one per line) and return them as a list.
    """
    print(f"Loading usernames from file {filename}...")
    start = time.time()
    usernames = []
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if max_users and i >= max_users:
                break  # stop reading
            usernames.append(line.strip())
    elapsed = time.time() - start
    print(f"Loaded {len(usernames)} usernames in {elapsed:.2f} seconds.")
    return usernames

def load_usernames_set(filename):
    """Use a generator to load large pickle file."""
    with open(filename, 'rb') as f:
        usernames_set = pickle.load(f)

    return usernames_set

def load_bloom_filter_in_chunks(filename, numUser):
    bloom_filter = BloomFilter(items_count=numUser, fp_prob=0.01)
    all_bits = []
    with open(filename, "rb") as f:
        while True:
            current_pos = f.tell()
            try:
                chunk = pickle.load(f)
                if not chunk:  # Check if chunk is null
                    break
                # bloom_filter.bit_array.extend(chunk)
                all_bits.extend(chunk) # Append the current chunk of the bit array to `bit_array`
                # print(f"Loaded BloomFilter chunk, total bits: {len(bloom_filter.bit_array)}")
                # print(f"Loaded BloomFilter chunk, total bits: {len(all_bits)}")
            except EOFError:
                if f.tell() == current_pos:
                    break

    if len(all_bits) >= bloom_filter.size:
        bloom_filter.bit_array.extend(all_bits[:bloom_filter.size])
        print(f"Loaded {len(all_bits)} bits in total, using first {bloom_filter.size} bits.")
    else:
        bloom_filter.bit_array.extend(all_bits[:len(all_bits)])
        print(f"Loaded {len(all_bits)} bits in total, using first {len(all_bits)} bits.")
    return bloom_filter

def load_cuckoo_filter_in_chunks(filename, numUser):
    cuckoo_filter = CuckooFilter(capacity=numUser)
    all_buckets = []

    with open(filename, "rb") as f:
        while True:
            try:
                current_pos = f.tell()
                chunk = pickle.load(f)
                # cuckoo_filter.buckets.extend(chunk)
                all_buckets.extend(chunk)  # Append the current chunk's bucket data to the `buckets` list
                # print(f"Loaded CuckooFilter chunk, total buckets: {len(cuckoo_filter.buckets)}")
                # print(f"Loaded CuckooFilter chunk, total buckets: {len(all_buckets)}")
            except EOFError:
                if f.tell() == current_pos:
                    # print("Reached EOF, breaking loop")
                    break

    cuckoo_filter.buckets.extend(all_buckets[:numUser])
    print(f"Loaded {len(all_buckets)} buckets in total, using first {numUser} buckets.")

    return cuckoo_filter

# Different data structures
def method_linear(usernames, new_username):

    return new_username in usernames

# def method_binary(sorted_usernames, new_username):
#
#     index = bisect.bisect_left(sorted_usernames, new_username)
#     return index < len(sorted_usernames) and sorted_usernames[index] == new_username

def method_binary(sorted_usernames, new_username):
    """
    Implements binary search to check if new_username exists in sorted_usernames.

    Parameters:
        sorted_usernames (list): A list of usernames sorted in ascending order.
        new_username (str): The username to search for.

    Returns:
        bool: True if new_username exists, False otherwise.
    """
    left, right = 0, len(sorted_usernames) - 1

    while left <= right:
        mid = (left + right) // 2
        if sorted_usernames[mid] == new_username:
            return True
        elif sorted_usernames[mid] < new_username:
            left = mid + 1
        else:
            right = mid - 1

    return False


def method_hash(usernames_set, new_username):

    return new_username in usernames_set


class TestSearchMethods(unittest.TestCase):
    """ Unittest class to test different search methods """
    max_users = iii * 1000000

    @classmethod
    def setUpClass(cls):
        """ Load usernames only once for all tests. """
        cls.usernames = load_usernames(DATA_FILE, cls.max_users)

        # Load BloomFilter and CuckooFilter
        start = time.time()
        cls.bloom_filter = load_bloom_filter_in_chunks(BLOOM_FILTER_FILE, cls.max_users)
        cls.cuckoo_filter = load_cuckoo_filter_in_chunks(CUCKOO_FILTER_FILE, cls.max_users)
        time_load = time.time() - start
        print(f"Load time : {time_load:.6f} seconds.")

        # Generate a new username
        # cls.fake = Faker()
        # cls.new_username = cls.fake.user_name() + "_" + str(cls.fake.random_int(1, len(cls.usernames)))
        cls.new_username = 'haoyu_5000001' # Set a non-existent username to ensure the worst-case search.
        print(f"Generated new username: {cls.new_username}")

    def test_1_linear_search(self):
        """ Test linear search """
        new_username = TestSearchMethods.new_username
        start = time.time()
        result = method_linear(self.usernames, new_username)
        time_linear = time.time() - start
        print(f"Method 1 (Linear Search): {'User name existed' if result else 'User name is available'}, search time: {time_linear:.6f} seconds")

    def test_2_binary_search(self):
        """ Test binary search """
        new_username = TestSearchMethods.new_username
        self.sorted_usernames = sorted(TestSearchMethods.usernames)
        start = time.perf_counter()
        result = method_binary(self.sorted_usernames, new_username)
        time_binary = time.perf_counter() - start
        print(f"Method 2 (Binary Search): {'User name existed' if result else 'User name is available'}, search time: {time_binary:.16f} seconds")

    def test_3_hash_search(self):
        """ Test hash search """
        new_username = TestSearchMethods.new_username
        self.usernames_set = set(TestSearchMethods.usernames)
        start = time.perf_counter()
        result = method_hash(self.usernames_set, new_username)
        time_hash = time.perf_counter() - start
        print(f"Method 3 (Hash Search): {'User name existed' if result else 'User name is available'}, search time: {time_hash:.16f} seconds")

    def test_4_bloomfilter_search(self):
        """ Test BloomFilter search """
        new_username = TestSearchMethods.new_username
        start = time.perf_counter()
        result = TestSearchMethods.bloom_filter.check(new_username)
        time_bloom = time.perf_counter() - start
        print(f"Method 4 (BloomFilter Search): {'User name existed' if result else 'User name is available'}, search time: {time_bloom:.16f} seconds")

    def test_5_cuckoofilter_search(self):
        """ Test CuckooFilter search """
        new_username = TestSearchMethods.new_username
        start = time.perf_counter()
        result = TestSearchMethods.cuckoo_filter.contains(new_username)
        time_cuckoo = time.perf_counter() - start
        print(f"Method 5 (CuckooFilter Search): {'User name existed' if result else 'User name is available'}, search time: {time_cuckoo:.16f} seconds")

if __name__ == '__main__':
    unittest.main()
