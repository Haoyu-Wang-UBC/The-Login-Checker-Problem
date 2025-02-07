import random


class CuckooFilter:
    """
    An implementation of a Cuckoo Filter.

    Attributes:
        capacity (int): Number of buckets in the filter.
        bucket_size (int): Maximum number of fingerprints that each bucket can store.
        fingerprint_size (int): Number of bits used for each fingerprint.
        max_kicks (int): Maximum number of relocations (kicks) allowed during an insertion.
        buckets (list): The filter's bucket array, where each bucket is a list that holds fingerprints.
    """

    def __init__(self, capacity=1024, bucket_size=4, fingerprint_size=8, max_kicks=500):
        """
        Initializes a new Cuckoo Filter.

        Parameters:
            capacity (int): Total number of buckets.
            bucket_size (int): Maximum entries per bucket.
            fingerprint_size (int): Fingerprint size in bits.
            max_kicks (int): Maximum number of displacements allowed during insertion.
        """
        self.capacity = capacity
        self.bucket_size = bucket_size
        self.fingerprint_size = fingerprint_size
        self.max_kicks = max_kicks
        # Initialize each bucket as an empty list.
        self.buckets = [[] for _ in range(self.capacity)]

    def _fingerprint(self, item):
        """
        Generates a fingerprint for the given item.

        Parameters:
            item: The element (e.g., string) for which to generate the fingerprint.

        Returns:
            int: The fingerprint as an integer (non-zero).
        """
        fp = hash(item) & ((1 << self.fingerprint_size) - 1)
        if fp == 0:
            fp = 1  # Avoid a fingerprint of zero.
        return fp

    def _index1(self, item):
        """
        Computes the first bucket index for the given item.

        Parameters:
            item: The item for which to compute the bucket index.

        Returns:
            int: The index of the first candidate bucket.
        """
        return hash(item) % self.capacity

    def _index2(self, index, fp):
        """
        Computes the second bucket index based on the first index and the fingerprint.

        Parameters:
            index (int): The first bucket index.
            fp (int): The fingerprint of the item.

        Returns:
            int: The index of the second candidate bucket.
        """
        # Here, we use XOR of the first index with the hash of the fingerprint,
        # then take modulo capacity.
        return (index ^ hash(fp)) % self.capacity

    def load_factor(self):
        """
        Computes the load factor of the Cuckoo Filter.

        Returns:
            float: The current load factor (0.0 - 1.0).
        """
        num_fingerprints = sum(len(bucket) for bucket in self.buckets)
        total_capacity = self.capacity * self.bucket_size
        return num_fingerprints / total_capacity

    def insert(self, item):
        """
        Inserts an item into the Cuckoo Filter.

        Parameters:
            item: The item to be inserted.

        Returns:
            bool: True if the insertion is successful; False otherwise.
        """
        fp = self._fingerprint(item)
        i1 = self._index1(item)
        i2 = self._index2(i1, fp)

        # Try inserting into the first bucket.
        if len(self.buckets[i1]) < self.bucket_size:
            self.buckets[i1].append(fp)
            return True

        # Try inserting into the second bucket.
        if len(self.buckets[i2]) < self.bucket_size:
            self.buckets[i2].append(fp)
            return True

        # Both candidate buckets are full; perform cuckoo kicking.
        i = random.choice([i1, i2])
        for _ in range(self.max_kicks):
            # Randomly choose a fingerprint in bucket i to kick out.
            j = random.randrange(len(self.buckets[i]))
            kicked_fp = self.buckets[i][j]
            self.buckets[i][j] = fp  # Place the new fingerprint here.
            fp = kicked_fp  # Set the kicked fingerprint as the one to reinsert.
            i = self._index2(i, fp)  # Compute the alternate bucket for the kicked fingerprint.
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp)
                return True
        # Insertion failed after maximum kicks.
        return False

    def contains(self, item):
        """
        Checks whether an item is possibly in the filter.

        Parameters:
            item: The item to search for.

        Returns:
            bool: True if the item might be in the filter (or is present), False if definitely not.
        """
        fp = self._fingerprint(item)
        i1 = self._index1(item)
        i2 = self._index2(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]

    def delete(self, item):
        """
        Deletes an item from the Cuckoo Filter.

        Parameters:
            item: The item to delete.

        Returns:
            bool: True if the item was found and deleted; False if not found.
        """
        fp = self._fingerprint(item)
        i1 = self._index1(item)
        i2 = self._index2(i1, fp)
        if fp in self.buckets[i1]:
            self.buckets[i1].remove(fp)
            return True
        if fp in self.buckets[i2]:
            self.buckets[i2].remove(fp)
            return True
        return False


# Example of how to use the CuckooFilter class:
if __name__ == "__main__":
    # Create a Cuckoo Filter instance with default parameters.
    cf = CuckooFilter(capacity=1024, bucket_size=4, fingerprint_size=8, max_kicks=500)

    # Insert some items.
    items_to_insert = ["apple", "banana", "cherry", "date", "elderberry"]
    for item in items_to_insert:
        success = cf.insert(item)
        print(f"Inserting '{item}': {'Success' if success else 'Failed'}")

    # Search for items using the contains() method.
    search_items = ["apple", "banana", "fig", "grape"]
    for item in search_items:
        if cf.contains(item):
            print(f"'{item}' is possibly in the filter.")
        else:
            print(f"'{item}' is definitely not in the filter.")

    # Delete an item and check again.
    if cf.delete("banana"):
        print("Deleted 'banana' successfully.")
    else:
        print("Failed to delete 'banana'.")

    if cf.contains("banana"):
        print("'banana' is still in the filter (or false positive).")
    else:
        print("'banana' has been removed from the filter.")
