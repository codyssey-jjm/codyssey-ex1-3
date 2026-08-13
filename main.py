"""Mini NPU Simulator의 실행 진입점."""

from pathlib import Path

from mini_npu.console import run_json_mode, run_manual_mode


def main() -> None:
    """Mini NPU Simulator를 실행한다."""
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3×3)")
    print("2. data.json 분석")

    mode = input("선택: ").strip()

    if mode == "1":
        run_manual_mode()
    elif mode == "2":
        run_json_mode(Path("data.json"))
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
