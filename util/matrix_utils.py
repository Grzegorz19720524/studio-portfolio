from typing import Any

Matrix = list[list[float]]


def zeros(rows: int, cols: int) -> Matrix:
    return [[0.0] * cols for _ in range(rows)]


def ones(rows: int, cols: int) -> Matrix:
    return [[1.0] * cols for _ in range(rows)]


def identity(n: int) -> Matrix:
    m = zeros(n, n)
    for i in range(n):
        m[i][i] = 1.0
    return m


def shape(matrix: Matrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def is_square(matrix: Matrix) -> bool:
    rows, cols = shape(matrix)
    return rows == cols


def transpose(matrix: Matrix) -> Matrix:
    rows, cols = shape(matrix)
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def add(a: Matrix, b: Matrix) -> Matrix:
    rows, cols = shape(a)
    return [[a[r][c] + b[r][c] for c in range(cols)] for r in range(rows)]


def subtract(a: Matrix, b: Matrix) -> Matrix:
    rows, cols = shape(a)
    return [[a[r][c] - b[r][c] for c in range(cols)] for r in range(rows)]


def scalar_multiply(matrix: Matrix, scalar: float) -> Matrix:
    return [[cell * scalar for cell in row] for row in matrix]


def multiply(a: Matrix, b: Matrix) -> Matrix:
    rows_a, cols_a = shape(a)
    rows_b, cols_b = shape(b)
    if cols_a != rows_b:
        raise ValueError(f"Incompatible shapes: ({rows_a}x{cols_a}) x ({rows_b}x{cols_b})")
    result = zeros(rows_a, cols_b)
    for i in range(rows_a):
        for j in range(cols_b):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(cols_a))
    return result


def trace(matrix: Matrix) -> float:
    if not is_square(matrix):
        raise ValueError("Trace requires a square matrix")
    return sum(matrix[i][i] for i in range(len(matrix)))


def determinant(matrix: Matrix) -> float:
    if not is_square(matrix):
        raise ValueError("Determinant requires a square matrix")
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    total = 0.0
    for col in range(n):
        minor = [[matrix[r][c] for c in range(n) if c != col] for r in range(1, n)]
        total += ((-1) ** col) * matrix[0][col] * determinant(minor)
    return total


def flatten(matrix: Matrix) -> list[float]:
    return [cell for row in matrix for cell in row]


def reshape(flat: list[float], rows: int, cols: int) -> Matrix:
    if len(flat) != rows * cols:
        raise ValueError(f"Cannot reshape {len(flat)} elements into ({rows}x{cols})")
    return [[flat[r * cols + c] for c in range(cols)] for r in range(rows)]


def get_row(matrix: Matrix, i: int) -> list[float]:
    return matrix[i]


def get_col(matrix: Matrix, j: int) -> list[float]:
    return [row[j] for row in matrix]


def map_matrix(fn, matrix: Matrix) -> Matrix:
    return [[fn(cell) for cell in row] for row in matrix]


def print_matrix(matrix: Matrix, width: int = 8) -> None:
    for row in matrix:
        print(" ".join(f"{cell:{width}.4g}" for cell in row))


if __name__ == "__main__":
    print("identity(3):")
    print_matrix(identity(3))

    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]

    print("\nadd:")
    print_matrix(add(a, b))

    print("\nsubtract:")
    print_matrix(subtract(a, b))

    print("\nmultiply:")
    print_matrix(multiply(a, b))

    print("\ntranspose:")
    print_matrix(transpose(a))

    print("\nscalar_multiply(a, 3):")
    print_matrix(scalar_multiply(a, 3))

    print("\ntrace(a):      ", trace(a))
    print("determinant(a):", determinant(a))
    print("shape(a):      ", shape(a))
    print("is_square(a):  ", is_square(a))

    print("\nflatten(a):    ", flatten(a))
    print("reshape back:  ", reshape(flatten(a), 2, 2))

    print("\nget_row(a, 0): ", get_row(a, 0))
    print("get_col(a, 1): ", get_col(a, 1))

    print("\nmap_matrix(x*2, a):")
    print_matrix(map_matrix(lambda x: x * 2, a))
