"""SKALA Python Practice 2 - 파일 I/O·예외 처리·Pydantic 검증 실습.

작성자: 김예찬
소속: 광주 캠퍼스 4반

프로그램 목적:
    교수자가 제공한 JSON 판매 데이터 전체를 안전하게 읽고 Pydantic v2 모델로
    검증한 뒤 정상 데이터와 오류 데이터를 CSV와 JSON으로 분리하여 저장한다.

입력 데이터:
    표준 JSON 리스트 형식의 교수 제공 ``Python_Practice2_Data.json``을 사용한다.
    원본의 전체 레코드를 그대로 검증하며 값을 수정하거나 오류 행을 만들지 않는다.

구현 기능:
    1. ``safe_load_json``의 try-except-finally 구조로 JSON 전체를 안전하게 읽는다.
    2. ``SalesRecord``가 문자열 공백과 0 이하의 금액을 Pydantic v2로 검증한다.
    3. 정상 레코드는 CSV, 오류 레코드는 한글이 유지되는 JSON으로 저장한다.
    4. 저장한 정상 CSV를 ``safe_load_csv``로 다시 읽어 동적으로 건수를 확인한다.

주요 변경 및 구현 내용:
    검증용 고정 데이터 대신 교수 제공 JSON 전체를 입력으로 사용하도록 변경했으며,
    정상·오류·재로딩 건수는 원본 검증 결과에 따라 동적으로 확인한다.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Annotated, TypeAlias

from pydantic import BaseModel, Field, StringConstraints, ValidationError


BASE_DIR = Path(__file__).parent
INPUT_JSON_PATH = BASE_DIR / "Python_Practice2_Data.json"
VALID_CSV_PATH = BASE_DIR / "valid_records.csv"
ERROR_JSON_PATH = BASE_DIR / "validation_errors.json"
CSV_FIELDS = ["month", "region", "amount", "category"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CsvRow: TypeAlias = dict[str, str]
RawRecord: TypeAlias = dict[str, object]
ValidationIssue: TypeAlias = dict[str, RawRecord | str]
NonEmptyString: TypeAlias = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1)
]


class SalesRecord(BaseModel):
    """판매 행의 필수 문자열과 양수 금액을 검증하는 Pydantic v2 모델이다."""

    month: NonEmptyString
    region: NonEmptyString
    amount: float = Field(gt=0)
    category: str | None = None


def safe_load_json(file_path: str | Path) -> list[RawRecord] | None:
    """JSON 파일의 전체 레코드를 안전하게 읽어 리스트로 반환한다.

    매개변수:
        file_path (str | Path): 읽을 JSON 파일 경로.
    반환값:
        list[dict] | None: 성공 시 JSON 레코드 목록, 실패 시 None.
    """
    try:
        with Path(file_path).open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            logger.error("JSON 최상위 데이터는 list 형식이어야 합니다.")
            return None
        logger.info("JSON 데이터 %d건을 읽었습니다.", len(data))
        return data
    except FileNotFoundError:
        logger.error("JSON 파일을 찾을 수 없습니다: %s", file_path)
        return None
    except json.JSONDecodeError as exc:
        logger.error("JSON 형식이 올바르지 않습니다: %s", exc)
        return None
    except (OSError, UnicodeError):
        logger.exception("JSON 파일을 읽는 중 오류가 발생했습니다.")
        return None
    finally:
        print("로딩 종료")


def safe_load_csv(file_path: str | Path) -> list[CsvRow] | None:
    """CSV 파일을 안전하게 읽어 딕셔너리 목록으로 반환한다.

    매개변수:
        file_path (str | Path): 읽을 CSV 파일 경로.
    반환값:
        list[dict] | None: 성공 시 CSV 행 목록, 실패 시 None.
    """
    try:
        with Path(file_path).open(encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
        logger.info("CSV 데이터 %d건을 읽었습니다.", len(rows))
        return rows
    except FileNotFoundError:
        # 사용자가 원인을 바로 확인할 수 있도록 누락된 경로를 함께 기록한다.
        logger.error("CSV 파일을 찾을 수 없습니다: %s", file_path)
        return None
    except (csv.Error, OSError, UnicodeError):
        # 예상하지 못한 읽기 오류는 원인 추적을 위해 traceback까지 기록한다.
        logger.exception("CSV 파일을 읽는 중 오류가 발생했습니다.")
        return None
    finally:
        print("로딩 종료")


def validate_records(
    raw_data: list[RawRecord],
) -> tuple[list[SalesRecord], list[ValidationIssue]]:
    """원본 JSON 행을 SalesRecord로 검증하여 정상과 오류 목록으로 분리한다.

    매개변수:
        raw_data (list[dict]): JSON에서 읽은 원본 판매 레코드 목록.
    반환값:
        tuple[list, list]: 정상 SalesRecord 목록과 원본 행·오류 내용 목록.
    """
    valid: list[SalesRecord] = []
    errors: list[ValidationIssue] = []

    for index, row in enumerate(raw_data, start=1):
        try:
            valid.append(SalesRecord.model_validate(row))
        except ValidationError as exc:
            logger.warning("%d번째 행 검증 오류:\n%s", index, exc)
            errors.append({"row": row, "error": str(exc)})

    logger.info("검증 완료: 정상 %d건, 오류 %d건", len(valid), len(errors))
    return valid, errors


def save_valid_records(records: list[SalesRecord], file_path: Path) -> None:
    """검증된 SalesRecord 목록을 model_dump 결과를 이용해 CSV로 저장한다.

    매개변수:
        records (list[SalesRecord]): 저장할 정상 판매 레코드 목록.
        file_path (Path): 정상 CSV 출력 경로.
    반환값:
        None.
    """
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(record.model_dump() for record in records)
    logger.info("정상 레코드 CSV를 저장했습니다: %s", file_path)


def save_validation_errors(errors: list[ValidationIssue], file_path: Path) -> None:
    """검증 오류와 원본 행을 사람이 읽기 쉬운 JSON으로 저장한다.

    매개변수:
        errors (list[dict]): 원본 행과 ValidationError 내용 목록.
        file_path (Path): 오류 JSON 출력 경로.
    반환값:
        None.
    """
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(errors, file, ensure_ascii=False, indent=2)
        file.write("\n")
    logger.info("검증 오류 JSON을 저장했습니다: %s", file_path)


def main() -> int:
    """JSON 로딩, 전체 검증, 결과 저장과 CSV 재로딩을 순서대로 실행한다.

    매개변수:
        없음.
    반환값:
        int: 정상 완료 시 0, 입력 또는 출력 파일 처리 실패 시 1.
    """
    assert safe_load_csv("존재하지_않는_파일.csv") is None

    raw_data = safe_load_json(INPUT_JSON_PATH)
    if raw_data is None:
        return 1

    valid, errors = validate_records(raw_data)
    assert len(valid) + len(errors) == len(raw_data)

    try:
        save_valid_records(valid, VALID_CSV_PATH)
        save_validation_errors(errors, ERROR_JSON_PATH)
    except (csv.Error, OSError, UnicodeError):
        logger.exception("결과 파일을 저장하는 중 오류가 발생했습니다.")
        return 1

    reloaded = safe_load_csv(VALID_CSV_PATH)
    if reloaded is None:
        logger.error("저장한 정상 CSV를 다시 불러오지 못했습니다.")
        return 1

    assert reloaded is not None
    assert len(reloaded) == len(valid)

    print(f"원본 JSON 데이터 건수: {len(raw_data)}건")
    print(f"정상 건수: {len(valid)}건")
    print(f"오류 건수: {len(errors)}건")
    print(f"정상 CSV 저장 경로: {VALID_CSV_PATH}")
    print(f"오류 JSON 저장 경로: {ERROR_JSON_PATH}")
    print(f"재로딩한 정상 데이터 건수: {len(reloaded)}건")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
