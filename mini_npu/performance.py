"""크기별 MAC 연산 시간 측정 기능."""

import time
from typing import Any, Dict, List, Tuple

from .mac import calculate_mac
from .models import Matrix

# 반복 횟수 상수: MAC 연산을 몇 번 반복 측정할지 정한 값
MEASUREMENT_REPETITIONS = 10

# data.json에 없는 3×3 성능 측정에 사용하는 기본 Cross 패턴과 필터
CROSS_PATTERN_3: Matrix = [
    [0.0, 1.0, 0.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 0.0],
]

CROSS_FILTER_3: Matrix = [
    [0.0, 1.0, 0.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 0.0],
]


def measure_mac_performance(
    pattern: Matrix,
    filter_matrix: Matrix,
) -> Dict[str, Any]:
    """MAC 연산을 10회 실행하고 한 번의 평균 실행 시간을 반환한다."""
    # 10회 반복을 시작하기 직전의 시간 기록
    start_time = time.perf_counter()
    
    # _: 반복 번호를 사용하지 않는다는 관례, 몇 번째 반복인지 알 필요 x
    for _ in range(MEASUREMENT_REPETITIONS):
        calculate_mac(pattern, filter_matrix)

    # 전체 경과 시간 계산
    elapsed_seconds = time.perf_counter() - start_time
    
    size = len(pattern)
    
    # 1회 평균 시간 계산
    # 초를 밀리초로 변환한 후 10으로 나눔
    average_ms = elapsed_seconds * 1000 / MEASUREMENT_REPETITIONS

    return {
        "size": size,
        "average_ms": average_ms,
        "operation_count": size * size, # 한 번의 MAC 연산에서 위치별 곱셈이 얼마나 일어나는가
    }


def measure_sizes(
    samples: Dict[int, Tuple[Matrix, Matrix]],
) -> List[Dict[str, Any]]:
    """
        samples에는 크기별 패던과 필터가 들어 있다
    """
    """여러 크기의 MAC 성능을 측정해 크기가 작은 순서로 반환한다."""
    results: List[Dict[str, Any]] = []

    # sorted() 사용시 키 값이 작은 순서로 정렬
    for size in sorted(samples):
        # 현재 크기에 해당하는 패턴과 필터 쌍을 가져온다
        pattern, filter_matrix = samples[size]
        # 크기별 성능 측정 실행
        results.append(measure_mac_performance(pattern, filter_matrix))

    return results
