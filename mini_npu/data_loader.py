"""JSON 데이터 로드, 스키마 검증 및 라벨 정규화 기능."""

import json
import re
from numbers import Real
from pathlib import Path
from typing import Any, Dict

from .mac import validate_square_matrix
from .models import Matrix


CROSS_LABEL = "Cross"
X_LABEL = "X"

# 정규 표현식 size로 시작, 행렬 크기, 마지막 번호, + 는 숫자가 한 개 이상
_PATTERN_KEY = re.compile(r"size_([0-9]+)_([0-9]+)")

_LABELS = {
    "cross": CROSS_LABEL,
    "+": CROSS_LABEL,
    CROSS_LABEL: CROSS_LABEL,
    "x": X_LABEL,
    X_LABEL: X_LABEL,
}


def load_json_data(path: Path) -> Dict[str, Any]:
    """JSON 파일을 읽고 분석에 필요한 최상위 객체를 검증한다."""
    with path.open(encoding="utf-8") as json_file:
        data = json.load(json_file)

    if not isinstance(data, dict):
        raise ValueError("JSON 최상위 데이터는 객체여야 합니다.")

    for field_name in ("filters", "patterns"):
        if field_name not in data:
            raise ValueError(f"JSON 최상위 데이터에 '{field_name}' 객체가 없습니다.")
        if not isinstance(data[field_name], dict):
            raise ValueError(f"JSON의 '{field_name}' 값은 객체여야 합니다.")

    return data


def normalize_label(label: str) -> str:
    """외부 라벨을 내부 표준 라벨인 Cross 또는 X로 변환한다."""
    if not isinstance(label, str):
        raise ValueError("라벨은 문자열이어야 합니다.")

    try:
        return _LABELS[label]
    except KeyError:
        raise ValueError(f"지원하지 않는 라벨입니다: {label!r}") from None


def extract_pattern_size(identifier: str) -> int:
    """size_{N}_{idx} 형식의 식별자에서 양수 크기 N을 추출한다."""
    if not isinstance(identifier, str):
        raise ValueError("패턴 식별자는 문자열이어야 합니다.")

    # fullmatch는 문자열 전체가 규칙과 일치하는지 확인
    match = _PATTERN_KEY.fullmatch(identifier)
    if match is None:
        raise ValueError(
            f"패턴 식별자는 'size_{{N}}_{{idx}}' 형식이어야 합니다: {identifier!r}"
        )

    # 첫 번째 괄호에 해당하는 값
    # ex) size_13_2 에서 13에 해당함
    size = int(match.group(1))
    if size <= 0:
        raise ValueError(f"패턴 크기는 양수여야 합니다: {identifier!r}")

    return size


def validate_matrix_data(
    matrix: Any,        # 검사할 실제 행렬
    required_size: int, # 행렬이 반드시 가져야 하는 크기
    field_name: str,    # 오류가 발생한 위치를 알려주기 위한 이름
) -> Matrix:
    """JSON 행렬의 구조, 숫자 타입 및 required_size를 검증한다."""
    if not isinstance(matrix, list):
        raise ValueError(f"'{field_name}' 값은 2차원 리스트여야 합니다.")

    # 각 행이 리스트인지 확인
    for row_index, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(
                f"'{field_name}'의 {row_index + 1}번째 행은 리스트여야 합니다."
            )
        # 모든 원소가 숫자인지 확인
        for column_index, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError(
                    f"'{field_name}'의 ({row_index + 1}, {column_index + 1}) 값은 "
                    "숫자여야 합니다."
                )

    try:
        actual_size = validate_square_matrix(matrix) # 정사각형인지 확인
    except ValueError as error:
        raise ValueError(f"'{field_name}' 행렬 오류: {error}") from None
    # 반드시 가져야 하는 크기와 실제 행렬 크기를 비교한다.
    if actual_size != required_size:
        raise ValueError(
            f"'{field_name}' 크기 불일치: 기대 {required_size}×{required_size}, "
            f"실제 {actual_size}×{actual_size}"
        )

    return [[float(value) for value in row] for row in matrix]


def build_pattern_case(
    identifier: str,
    raw_case: Dict[str, Any],
    raw_filters: Dict[str, Any],
) -> Dict[str, Any]:
    """
    한 패턴과 같은 크기의 필터를 검증해 사전으로 구성한다.
    실제 검증 처리는 _build_pattern_case()에 맡김
    함수를 둘로 나눈 이유는 오류 메시지에 케이스 이름을 붙이기 위함
    """
    try:
        return _build_pattern_case(identifier, raw_case, raw_filters)
    except ValueError as error:
        raise ValueError(f"케이스 {identifier!r} 오류: {error}") from None


def _build_pattern_case(
    identifier: str,            # 패턴 이름
    raw_case: Dict[str, Any],   # 해당 패턴의 input과 expected    
    raw_filters: Dict[str, Any],# JSON의 전체 filters
) -> Dict[str, Any]:
    """식별자 접두사 없이 한 패턴 케이스를 검증하고 구성한다."""
    size = extract_pattern_size(identifier)

    if not isinstance(raw_case, dict):
        raise ValueError("패턴 항목은 객체여야 합니다.")
    for field_name in ("input", "expected"):
        if field_name not in raw_case:
            raise ValueError(f"패턴 항목에 '{field_name}' 값이 없습니다.")

    if not isinstance(raw_filters, dict):
        raise ValueError("'filters' 값은 객체여야 합니다.")

    # 필터 목록에 찾으려는 필터가 존재하는가
    filter_group_name = f"size_{size}"
    if filter_group_name not in raw_filters:
        raise ValueError(f"'{filter_group_name}' 필터 묶음이 없습니다.")

    # 찾은 필터에 값이 dict 형태인가
    raw_filter_group = raw_filters[filter_group_name]
    if not isinstance(raw_filter_group, dict):
        raise ValueError(f"'{filter_group_name}' 필터 묶음은 객체여야 합니다.")

    # 이름을 Cross, X로 통일한 필터들을 담아둘 변수
    normalized_filters: Dict[str, Any] = {}

    # 선택한 크기의 필터 묶음에 들어 있는 필터를 하나씩 확인한다.
    # raw_label에는 원래 필터 이름이, filter_matrix에는 해당 필터 행렬이 들어온다.
    for raw_label, filter_matrix in raw_filter_group.items():
        # 원래 필터 이름을 프로그램 내부에서 사용하는 표준 이름으로 바꾼다.
        # "cross"는 "Cross"로, "x"는 "X"로 변환된다.
        normalized_label = normalize_label(raw_label)

        # cross, Cross 통일했을때 같은 이름을 가진 필터가 있는지 검증
        if normalized_label in normalized_filters:
            raise ValueError(
                f"'{filter_group_name}'에 {normalized_label} 필터가 중복되었습니다."
            )

        # 표준 필터 이름을 키로 사용하고 원래 필터 행렬을 값으로 저장한다.
        normalized_filters[normalized_label] = filter_matrix

    # Cross, X 필터 모두 있는지 확인
    for label in (CROSS_LABEL, X_LABEL):
        if label not in normalized_filters:
            raise ValueError(f"'{filter_group_name}'에 {label} 필터가 없습니다.")

    # 패턴 행렬 검증
    pattern = validate_matrix_data(raw_case["input"], size, f"{identifier}.input")

    # cross 필터 검증
    cross_filter = validate_matrix_data(
        normalized_filters[CROSS_LABEL],
        size,
        f"{filter_group_name}.Cross",
    )

    # x 필터 검증
    x_filter = validate_matrix_data(
        normalized_filters[X_LABEL],
        size,
        f"{filter_group_name}.X",
    )

    # JSON의 expected 값도 비교에 사용할 표준 라벨로 바꾼다.
    expected = normalize_label(raw_case["expected"])
    return {
        "identifier": identifier,
        "size": size,
        "pattern": pattern,
        "cross_filter": cross_filter,
        "x_filter": x_filter,
        "expected": expected,
    }
