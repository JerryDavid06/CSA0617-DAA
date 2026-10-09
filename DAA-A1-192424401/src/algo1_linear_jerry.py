"""
Algorithm 1 - Iterative Linear Search
Strategy: Brute-force / sequential search
"""

def linear_search(records, target):
    comparisons = 0

    for value in records:
        comparisons += 1
        if value == target:
            return True, comparisons

    return False, comparisons
