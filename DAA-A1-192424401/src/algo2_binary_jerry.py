"""
Algorithm 2 - Recursive Binary Search
Strategy: Divide-and-conquer
Precondition: records must be sorted in ascending order.
"""

def binary_search_recursive(records, low, high, target):
    # Base case: empty search interval.
    if low > high:
        return False, 0

    mid = low + (high - low) // 2
    comparisons = 1

    if records[mid] == target:
        return True, comparisons

    if target < records[mid]:
        found, child_comparisons = binary_search_recursive(
            records, low, mid - 1, target
        )
    else:
        found, child_comparisons = binary_search_recursive(
            records, mid + 1, high, target
        )

    return found, comparisons + child_comparisons

def binary_search(records, target):
    return binary_search_recursive(records, 0, len(records) - 1, target)
