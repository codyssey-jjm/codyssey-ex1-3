"""3×3 사용자 입력 모드와 콘솔 출력 기능."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .data_loader import build_pattern_case, load_json_data
from .mac import calculate_mac, select_label
from .models import UNDECIDED, Matrix
from .performance import (
    CROSS_FILTER_3,
    CROSS_PATTERN_3,
    measure_mac_performance,
    measure_sizes,
)
from .report import analyze_patterns


INPUT_SIZE = 3

# 함수 이름 앞에 _는 현재 모듈 내부에서만 사용하는 함수라는 Python에서의 관례
# Java의 private처럼 접근을 강제로 막지는 않는다.
def _input_error_message(size: int) -> str:
    return f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(raw_value: str, size: int = INPUT_SIZE) -> List[float]:
    """공백으로 구분된 한 줄을 정해진 개수의 실수로 변환한다."""
    # 인자 없는 split()은 앞뒤 공백과 연속 공백을 자동으로 제거한다.
    values = raw_value.split()
    if len(values) != size:
        raise ValueError(_input_error_message(size))

    try:
        return [float(value) for value in values]
    except ValueError:
        # 숫자 변환 오류도 열 개수 오류와 동일한 사용자 안내 문구로 처리한다.
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

    # 하나의 패턴을 필터 A와 B에 각각 적용해 비교할 점수를 계산한다.
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    result = select_label(score_a, score_b, "A", "B")
    
    # 입력받은 패턴과 필터A를 사용해 평균시간 측정
    performance = measure_mac_performance(pattern, filter_a)

    # 내부 표준값은 사용자 입력 모드에 맞는 한글 문구로 바꾼다.
    displayed_result = "판정 불가" if result == UNDECIDED else result

    print("\n[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {displayed_result}")
    print(f"연산 시간(평균/10회): {performance['average_ms']} ms")


def run_json_mode(path: Path) -> None:
    """JSON 패턴을 분석하고 성능 및 전체 결과를 출력한다."""
    try:
        data = load_json_data(path)
    except FileNotFoundError:               # 파일이 없는 경우
        print(f"파일 오류: '{path}' 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as error:   # JSON 문법이 잘못된 경우
        print(f"JSON 형식 오류: {error}")
        return
    except ValueError as error:             # 최상위 필터 또는 패턴 구조가 잘못된 경우
        print(f"JSON 구조 오류: {error}")
        return

    summary = analyze_patterns(data)

    print("\n[1] 패턴 분석")
    # summary["results"]에는 정상 계산 결과와 검증 오류 결과가 모두 들어 있다.
    for result in summary["results"]:
        print(f"\n--- {result['identifier']} ---")
        status = "PASS" if result["passed"] else "FAIL"

        # 정상 계산 결과에는 두 점수와 판정이 들어 있다.
        # 검증 중 오류가 난 결과에는 cross_score가 없으므로 FAIL과 사유만 출력한다.
        if "cross_score" in result:
            print(f"Cross 점수: {result['cross_score']}")
            print(f"X 점수: {result['x_score']}")
            print(
                f"판정: {result['prediction']} | "
                f"expected: {result['expected']} | {status}"
            )
        else:
            print(f"결과: {status}")

        if not result["passed"]:
            print(f"사유: {result['reason']}")

    # data.json에는 3×3 데이터가 없으므로 performance.py의 기본 3×3 샘플을 사용한다.
    samples: Dict[int, Tuple[Matrix, Matrix]] = {
        3: (CROSS_PATTERN_3, CROSS_FILTER_3),
    }

    raw_filters = data["filters"]
    # 각 크기에서 처음 검증을 통과한 패턴과 Cross 필터 한 쌍만 측정에 사용한다.
    for identifier, raw_case in data["patterns"].items():
        try:
            case = build_pattern_case(identifier, raw_case, raw_filters)
        except ValueError:
            # 잘못된 케이스는 성능 측정 샘플로 사용할 수 없으므로 건너뛴다.
            continue

        size = case["size"]
        # 같은 크기의 샘플이 이미 있으면 중복해서 측정하지 않는다.
        if size not in samples:
            samples[size] = (case["pattern"], case["cross_filter"])

    # 준비한 크기별 샘플을 각각 10회 측정하고 평균 시간을 구한다.
    performance_results = measure_sizes(samples)

    print("\n[2] 성능 분석 (평균/10회)")
    print("크기       평균 시간(ms)    연산 횟수")
    # 성능 결과는 measure_sizes()에서 크기가 작은 순서로 정렬되어 있다.
    for result in performance_results:
        size = result["size"]
        print(
            f"{size}×{size:<6} "
            f"{result['average_ms']:<16} "
            f"{result['operation_count']}"
        )

    # analyze_patterns()에서 집계한 전체, 통과, 실패 개수를 출력한다.
    print("\n[3] 결과 요약")
    print(f"총 테스트: {summary['total']}개")
    print(f"통과: {summary['passed']}개")
    print(f"실패: {summary['failed']}개")

    # 전체 결과 중 실패한 항목만 골라 실패 케이스 목록을 만든다.
    failed_results: List[Dict[str, Any]] = [
        result for result in summary["results"] if not result["passed"]
    ]
    if failed_results:
        print("\n실패 케이스:")
        for result in failed_results:
            print(f"- {result['identifier']}: {result['reason']}")
