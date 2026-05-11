import heapq
from typing import Any


def is_sorted(arr: list, reverse: bool = False) -> bool:
    if reverse:
        return all(arr[i] >= arr[i + 1] for i in range(len(arr) - 1))
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))


def bubble_sort(arr: list) -> list:
    a = list(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def selection_sort(arr: list) -> list:
    a = list(arr)
    n = len(a)
    for i in range(n):
        min_idx = min(range(i, n), key=lambda x: a[x])
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def insertion_sort(arr: list) -> list:
    a = list(arr)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]


def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return list(arr)
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def heap_sort(arr: list) -> list:
    a = list(arr)
    heapq.heapify(a)
    return [heapq.heappop(a) for _ in range(len(a))]


def shell_sort(arr: list) -> list:
    a = list(arr)
    gap = len(a) // 2
    while gap > 0:
        for i in range(gap, len(a)):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2
    return a


def counting_sort(arr: list[int]) -> list[int]:
    if not arr:
        return []
    lo, hi = min(arr), max(arr)
    counts = [0] * (hi - lo + 1)
    for v in arr:
        counts[v - lo] += 1
    return [lo + i for i, c in enumerate(counts) for _ in range(c)]


def radix_sort(arr: list[int]) -> list[int]:
    if not arr:
        return []
    a = list(arr)
    max_val = max(abs(v) for v in a)
    exp = 1
    while max_val // exp > 0:
        buckets = [[] for _ in range(10)]
        for v in a:
            buckets[(v // exp) % 10].append(v)
        a = [v for bucket in buckets for v in bucket]
        exp *= 10
    return a


def binary_search(arr: list, target: Any) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print("original:       ", data)
    print("bubble_sort:    ", bubble_sort(data))
    print("selection_sort: ", selection_sort(data))
    print("insertion_sort: ", insertion_sort(data))
    print("merge_sort:     ", merge_sort(data))
    print("quick_sort:     ", quick_sort(data))
    print("heap_sort:      ", heap_sort(data))
    print("shell_sort:     ", shell_sort(data))
    print("counting_sort:  ", counting_sort(data))
    print("radix_sort:     ", radix_sort(data))

    sorted_data = merge_sort(data)
    print("\nbinary_search(sorted, 25):", binary_search(sorted_data, 25))
    print("binary_search(sorted, 99):", binary_search(sorted_data, 99))

    print("\nis_sorted([1,2,3]):        ", is_sorted([1, 2, 3]))
    print("is_sorted([3,2,1]):        ", is_sorted([3, 2, 1]))
    print("is_sorted([3,2,1],reverse):", is_sorted([3, 2, 1], reverse=True))
