"""JSON 패턴의 판정, PASS/FAIL 처리 및 결과 집계 기능."""

from typing import Any, Dict, List

from .data_loader import CROSS_LABEL, X_LABEL, build_pattern_case
from .mac import calculate_mac, select_label


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """검증된 패턴 케이스의 점수, 판정 및 PASS/FAIL 결과를 반환한다."""
    """
        예시
        case = {
            "identifier": "size_5_1",   # 케이스 이름
            "size": 5,                  # 행렬 크기
            "pattern": [[...]],         # 판정할 패턴 행렬
            "cross_filter": [[...]],    # Cross 필터 행렬
            "x_filter": [[...]],        # X 필터 행렬
            "expected": "X",            # JSON에 기록된 예상 정답
        }
    """
    cross_score = calculate_mac(case["pattern"], case["cross_filter"])
    x_score = calculate_mac(case["pattern"], case["x_filter"])
    # 두 점수로 판정
    prediction = select_label(
        cross_score,
        x_score,
        CROSS_LABEL,
        X_LABEL,
    )

    expected = case["expected"]
    passed = prediction == expected
    result = {
        "identifier": case["identifier"],
        "cross_score": cross_score,
        "x_score": x_score,
        "prediction": prediction,
        "expected": expected,
        "passed": passed,
    }

    if not passed:
        result["reason"] = (
            f"판정 {prediction}이 expected {expected}와 다릅니다."
        )

    return result


def analyze_patterns(data: Dict[str, Any]) -> Dict[str, Any]:
    """모든 JSON 패턴을 개별 처리하고 전체 PASS/FAIL 수를 집계한다."""
    raw_filters = data["filters"]
    raw_patterns = data["patterns"]
    results: List[Dict[str, Any]] = []

    for identifier, raw_case in raw_patterns.items():
        try:
            case = build_pattern_case(identifier, raw_case, raw_filters)
            result = evaluate_case(case)
        except ValueError as error:
            # 한 케이스의 오류를 FAIL로 기록하고 다음 케이스를 계속 처리한다.
            result = {
                "identifier": identifier,
                "passed": False,
                "reason": str(error),
            }
        results.append(result)
    # 전체 결과 수 집계
    total_count = len(results)
    # 결과를 하나씩 확인하면서 passed가 True인 결과마다 1을 더함
    passed_count = sum(1 for result in results if result["passed"])

    return {
        "results": results,
        "total": total_count,
        "passed": passed_count,
        "failed": total_count - passed_count,
    }
