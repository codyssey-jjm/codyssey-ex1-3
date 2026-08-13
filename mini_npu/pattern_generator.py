"""크기 N에 맞는 Cross 및 X 패턴 생성 기능."""

from .models import Matrix


def generate_cross_pattern(size: int) -> Matrix:
    """가운데 행과 열이 1.0인 N×N Cross 패턴을 반환한다."""
    if size < 1:
        raise ValueError("패턴 크기는 1 이상이어야 합니다.")

    center = size // 2
    pattern: Matrix = []

    for row in range(size):
        pattern_row = []
        for column in range(size):
            # 현재 행이 가운데 행인가 현재 열이 가운데 열인가? 둘 중 하나라도 만족시 1.0 저장
            value = 1.0 if row == center or column == center else 0.0
            pattern_row.append(value)
        pattern.append(pattern_row)

    return pattern


def generate_x_pattern(size: int) -> Matrix:
    """양쪽 대각선이 1.0인 N×N X 패턴을 반환한다."""
    if size < 1:
        raise ValueError("패턴 크기는 1 이상이어야 합니다.")

    pattern: Matrix = []

    for row in range(size):
        pattern_row = []
        for column in range(size):
            # 대각선 위치 확인
            # 행 번호와 열 번호가 같은 위치, 행 열 번호를 더해 size-1이 되는 위치
            is_diagonal = row == column or row + column == size - 1
            pattern_row.append(1.0 if is_diagonal else 0.0)
        pattern.append(pattern_row)

    return pattern
