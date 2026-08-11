"""3×3 사용자 입력 모드와 콘솔 출력 기능."""

from typing import List

from .mac import calculate_mac, select_label
from .models import UNDECIDED, Matrix


INPUT_SIZE = 3


def _input_error_message(size: int) -> str:
    return f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(raw_value: str, size: int = INPUT_SIZE) -> List[float]:
    """공백으로 구분된 한 줄을 정해진 개수의 실수로 변환한다."""
    values = raw_value.split()
    if len(values) != size:
        raise ValueError(_input_error_message(size))

    try:
        return [float(value) for value in values]
    except ValueError:
        raise ValueError(_input_error_message(size)) from None


def read_matrix(name: str, size: int = INPUT_SIZE) -> Matrix:
    """올바른 행이 정해진 개수만큼 모일 때까지 행렬을 입력받는다."""
    print(f"{name} ({size}줄 입력, 공백 구분)")
    matrix: Matrix = []

    # 잘못 입력한 행은 저장하지 않고 같은 행부터 다시 입력받는다.
    while len(matrix) < size:
        try:
            matrix.append(parse_row(input(), size))
        except ValueError as error:
            print(error)

    return matrix


def run_manual_mode() -> None:
    """3×3 필터 두 개와 패턴을 입력받아 MAC 점수와 판정을 출력한다."""
    print("[1] 필터 입력")
    filter_a = read_matrix("필터 A")
    print("필터 A 저장 완료")
    filter_b = read_matrix("필터 B")
    print("필터 B 저장 완료")

    print("\n[2] 패턴 입력")
    pattern = read_matrix("패턴")

    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    result = select_label(score_a, score_b, "A", "B")

    # 내부 표준값은 사용자 입력 모드에 맞는 한글 문구로 바꾼다.
    displayed_result = "판정 불가" if result == UNDECIDED else result

    print("\n[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {displayed_result}")
