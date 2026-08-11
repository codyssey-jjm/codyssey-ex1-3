"""Mini NPU Simulator에서 공통으로 사용하는 데이터 타입과 상수."""

from typing import List

# 2차원 숫자 배열 타입 별칭
Matrix = List[List[float]]

# 점수 비교시 허용 오차
EPSILON = 1e-9

# 점수가 같거나 epsilon 범위 안에 있을 때 반환하는 결과
UNDECIDED = "UNDECIDED"
