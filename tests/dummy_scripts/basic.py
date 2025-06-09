def count_even_numbers_in_matrix(matrix):
    even_count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] % 2 == 0:
                even_count += 1
    return even_count


def duplicate_and_sort_list(lst):
    new_list = []
    for item in lst:
        new_list.append(item)
    for item in lst:
        new_list.append(item)
    new_list.sort()
    return new_list


def main():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print("Even numbers in matrix:", count_even_numbers_in_matrix(matrix))

    original_list = [3, 1, 4]
    print("Duplicated and sorted list:", duplicate_and_sort_list(original_list))


if __name__ == "__main__":
    main()
