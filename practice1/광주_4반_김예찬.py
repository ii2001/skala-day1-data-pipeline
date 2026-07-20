"""SKALA Python Practice 1 - 자료구조 집계·컴프리헨션·제너레이터 실습.

작성자: 김예찬
소속: 광주 캠퍼스 4반

프로그램 목적:
    판매 거래 데이터를 안전하게 불러온 뒤 Python 표준 자료구조와 컴프리헨션,
    제너레이터를 이용해 조건별 필터링과 다양한 매출 집계를 수행한다.

입력 파일:
    이 프로그램과 같은 디렉터리의 ``Python_Practice1_Data.json``을 사용한다.
    파일 확장자는 json이지만 실제 내용은 ``sales = [...]`` 형태의 Python 데이터이다.

주요 구현 내용:
    1. ``sales =`` 오른쪽의 리스트만 분리하고 ``ast.literal_eval``로 안전하게 파싱한다.
    2. 전체 자료형, 거래별 필수 키, 문자열 필드와 amount의 숫자 여부를 검증한다.
    3. 컴프리헨션, Counter, defaultdict를 사용해 거래와 매출을 조건별로 집계한다.
    4. 리스트와 제너레이터의 메모리 크기를 비교하고 월별·카테고리별 Top 3를 구한다.
    5. 주요 집계와 정렬 결과는 assert로 검증하며 오류 원인은 한국어로 출력한다.
"""

import ast
import sys
from collections import Counter, defaultdict
from numbers import Real
from pathlib import Path
from pprint import pprint


DATA_PATH = Path(__file__).with_name("Python_Practice1_Data.json")
REQUIRED_KEYS = {"region", "category", "amount", "month"}
EXPECTED_REGION_TOTALS = {
    "서울": 20060,
    "부산": 10930,
    "대구": 12660,
    "인천": 14530,
    "광주": 9620,
    "대전": 11140,
    "울산": 11700,
    "세종": 10820,
}


class SalesDataError(Exception):
    """판매 데이터의 로딩 또는 검증 실패를 나타내는 예외이다."""


def load_sales(file_path):
    """판매 데이터 파일을 안전하게 읽고 검증한다.

    매개변수:
        file_path (Path): 읽을 판매 데이터 파일 경로.
    반환값:
        list: 검증을 통과한 거래 딕셔너리 목록.
    """
    try:
        content = file_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SalesDataError(f"데이터 파일을 찾을 수 없습니다: {file_path}") from exc
    except (OSError, UnicodeError) as exc:
        raise SalesDataError(f"데이터 파일을 읽을 수 없습니다: {exc}") from exc

    if not content:
        raise SalesDataError("데이터 파일이 비어 있습니다.")

    variable_name, separator, data_text = content.partition("=")
    if not separator or variable_name.strip() != "sales":
        raise SalesDataError("파일은 'sales = [...]' 형식이어야 합니다.")

    try:
        sales = ast.literal_eval(data_text.strip())
    except (SyntaxError, ValueError) as exc:
        raise SalesDataError(f"판매 데이터 형식이 올바르지 않습니다: {exc}") from exc

    validate_sales(sales)
    return sales


def validate_sales(sales):
    """판매 데이터의 전체 구조와 각 거래의 필수 값을 검사한다.

    매개변수:
        sales: 검사할 판매 데이터 객체.
    반환값:
        None: 문제가 없으면 반환하며, 잘못된 데이터는 SalesDataError를 발생시킨다.
    """
    if not isinstance(sales, list):
        raise SalesDataError("sales 데이터는 list 형식이어야 합니다.")

    for index, sale in enumerate(sales, start=1):
        if not isinstance(sale, dict):
            raise SalesDataError(f"{index}번째 거래는 dict 형식이어야 합니다.")

        missing_keys = REQUIRED_KEYS - sale.keys()
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise SalesDataError(f"{index}번째 거래에 필수 키가 없습니다: {missing}")

        for key in ("region", "category", "month"):
            if not isinstance(sale[key], str) or not sale[key].strip():
                raise SalesDataError(
                    f"{index}번째 거래의 {key} 값은 비어 있지 않은 문자열이어야 합니다."
                )

        if isinstance(sale["amount"], bool) or not isinstance(sale["amount"], Real):
            raise SalesDataError(f"{index}번째 거래의 amount는 숫자여야 합니다.")


def high_amount_generator(sales):
    """금액이 1000보다 큰 거래를 한 건씩 생성한다.

    매개변수:
        sales (list): 검증된 거래 딕셔너리 목록.
    반환값:
        generator: 조건을 만족하는 거래를 지연 생성하는 iterator.
    """
    for sale in sales:
        if sale["amount"] > 1000:
            yield sale


def main():
    """데이터를 불러와 모든 집계 실습을 실행하고 결과를 출력한다.

    매개변수:
        없음.
    반환값:
        int: 정상 실행은 0, 데이터 오류가 발생하면 1.
    """
    try:
        sales = load_sales(DATA_PATH)
    except SalesDataError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    print(f"전체 거래 건수: {len(sales)}건")

    high_value_sales = [sale for sale in sales if sale["amount"] >= 1000]
    print("\n[amount가 1000 이상인 거래]")
    pprint(high_value_sales)
    print(f"필터링 거래 건수: {len(high_value_sales)}건")

    regions = {sale["region"] for sale in sales}
    region_total = {
        region: sum(sale["amount"] for sale in sales if sale["region"] == region)
        for region in regions
    }
    assert region_total == EXPECTED_REGION_TOTALS, "지역별 총매출 집계가 정확하지 않습니다."
    print("\n[지역별 총매출]")
    pprint(region_total, sort_dicts=True)

    region_counts = Counter(sale["region"] for sale in sales)
    region_ranking = region_counts.most_common()
    assert all(
        region_ranking[index][1] >= region_ranking[index + 1][1]
        for index in range(len(region_ranking) - 1)
    ), "지역별 거래 건수가 내림차순으로 정렬되지 않았습니다."
    print("\n[지역별 전체 거래 건수 - 많은 순]")
    pprint(region_ranking)

    category_amounts = defaultdict(list)
    for sale in sales:
        category_amounts[sale["category"]].append(sale["amount"])
    print("\n[카테고리별 amount 목록]")
    pprint(dict(category_amounts), sort_dicts=True)

    # 제너레이터는 한 번 순회하면 소진되는 일회성 iterator이다.
    generated_sales = high_amount_generator(sales)
    generated_sales_list = [sale for sale in sales if sale["amount"] > 1000]
    list_size = sys.getsizeof(generated_sales_list)
    generator_size = sys.getsizeof(generated_sales)
    assert generator_size < list_size, "제너레이터가 리스트보다 작지 않습니다."
    print("\n[리스트와 제너레이터 메모리 비교]")
    print(f"리스트 객체 크기: {list_size} bytes")
    print(f"제너레이터 객체 크기: {generator_size} bytes")

    monthly_category_totals = defaultdict(int)
    for sale in sales:
        key = (sale["month"], sale["category"])
        monthly_category_totals[key] += sale["amount"]

    monthly_category_sales = {
        key: total for key, total in monthly_category_totals.items()
    }
    assert sum(monthly_category_sales.values()) == sum(
        sale["amount"] for sale in sales
    ), "월별·카테고리별 총매출 집계가 정확하지 않습니다."
    print("\n[월별·카테고리별 총매출]")
    pprint(monthly_category_sales, sort_dicts=True)

    top3 = sorted(
        monthly_category_sales.items(), key=lambda item: item[1], reverse=True
    )[:3]
    assert len(top3) == 3, "상위 3개 집계 결과가 필요합니다."
    assert all(
        top3[index][1] >= top3[index + 1][1] for index in range(len(top3) - 1)
    ), "Top 3가 금액 내림차순으로 정렬되지 않았습니다."
    print("\n[월별·카테고리별 총매출 Top 3]")
    pprint(top3)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
