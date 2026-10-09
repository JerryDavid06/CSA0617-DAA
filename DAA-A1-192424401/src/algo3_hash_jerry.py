"""
Algorithm 3 - Hash Table Search
Strategy: Direct-access / hashing
Preprocessing: Build a hash table (Python dictionary) from registration numbers.
"""

def build_hash_table(records):
    # Key = registration number, value = True.
    # Construction cost is measured separately by benchmark.py.
    return {value: True for value in records}

def hash_search(hash_table, target):
    # One dictionary membership operation is counted as one key lookup.
    return target in hash_table, 1
