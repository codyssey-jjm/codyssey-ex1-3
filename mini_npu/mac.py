"""행렬 검증, MAC 연산 및 점수 판정 기능."""

from .models import EPSILON, UNDECIDED, Matrix


def validate_square_matrix(matrix: Matrix) -> int:
    """행렬이 비어 있지 않은 정사각형인지 검증하고 크기를 반환한다."""
    if not matrix:
        raise ValueError("행렬은 비어 있을 수 없습니다.")

    size = len(matrix)
    for row in matrix:
        if len(row) != size:
            raise ValueError("행렬은 행과 열의 크기가 같은 정사각형이어야 합니다.")

    return size


def calculate_mac(pattern: Matrix, filter_matrix: Matrix) -> float:
    """패턴과 필터의 같은 위치 값을 곱해 누적한 MAC 점수를 반환한다."""
    pattern_size = validate_square_matrix(pattern)
    filter_size = validate_square_matrix(filter_matrix)

    if pattern_size != filter_size:
        raise ValueError("패턴과 필터의 크기가 같아야 합니다.")

    score = 0.0
    for row in range(pattern_size):
        for column in range(pattern_size):
            score += pattern[row][column] * filter_matrix[row][column]

    return score


def select_label(
    score_a: float,
    score_b: float,
    label_a: str,
    label_b: str,
    epsilon: float = EPSILON,
) -> str:
    """두 점수를 epsilon 기준으로 비교해 선택된 라벨을 반환한다."""
    if epsilon < 0:
        raise ValueError("epsilon은 음수일 수 없습니다.")

    difference = abs(score_a - score_b)
    if difference == 0 or difference < epsilon:
        return UNDECIDED
    if score_a > score_b:
        return label_a
    return label_b
