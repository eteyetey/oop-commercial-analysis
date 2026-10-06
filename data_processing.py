
from pathlib import Path

import pandas as pd
from pyproj import Transformer


# ==========================================
# 1. 파일 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# 2. CSV 파일 읽기
# ==========================================

def read_csv_file(file_path):
    """한글 인코딩이 다른 CSV 파일도 읽을 수 있도록 처리"""

    encodings = ["utf-8-sig", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"[읽기 성공] {file_path.name} ({encoding})")
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError(f"CSV 인코딩을 확인해 주세요: {file_path}")


# ==========================================
# 3. 데이터 전처리
# ==========================================

def preprocess_data(df):
    # 컬럼 이름 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 문자열 데이터의 앞뒤 공백 제거
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    # 완전히 동일한 중복 행 제거
    before = len(df)
    df = df.drop_duplicates().copy()
    removed = before - len(df)

    print(f"중복 제거: {removed}개")
    print(f"현재 행 개수: {len(df):,}개")

    return df


# ==========================================
# 4. 상권 위치 데이터 전처리 및 좌표 변환
# ==========================================

def process_location():
    location_path = DATA_DIR / "data_location.csv"

    if not location_path.exists():
        raise FileNotFoundError(
            f"위치 파일을 찾을 수 없습니다: {location_path}"
        )

    location = preprocess_data(read_csv_file(location_path))

    required_columns = [
        "상권_코드",
        "엑스좌표_값",
        "와이좌표_값",
    ]

    for column in required_columns:
        if column not in location.columns:
            raise ValueError(
                f"data_location.csv에 '{column}' 컬럼이 없습니다."
            )

    # 좌표를 숫자로 변환
    location["엑스좌표_값"] = pd.to_numeric(
        location["엑스좌표_값"], errors="coerce"
    )
    location["와이좌표_값"] = pd.to_numeric(
        location["와이좌표_값"], errors="coerce"
    )

    # 상권 코드를 문자열로 통일해 병합 오류 방지
    location["상권_코드"] = (
        location["상권_코드"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    # 상권 코드가 중복된 경우 첫 번째 행만 사용
    location = location.drop_duplicates(
        subset=["상권_코드"], keep="first"
    ).copy()

    # 원본 좌표가 모두 존재하는 행만 변환
    valid = (
        location["엑스좌표_값"].notna()
        & location["와이좌표_값"].notna()
    )

    # 주의: EPSG:5181은 임시 설정입니다.
    # 원본 데이터의 좌표계가 EPSG:5181인지 확인한 후 사용하세요.
    source_crs = "EPSG:5181"

    transformer = Transformer.from_crs(
        source_crs,
        "EPSG:4326",
        always_xy=True,
    )

    longitude, latitude = transformer.transform(
        location.loc[valid, "엑스좌표_값"].to_numpy(),
        location.loc[valid, "와이좌표_값"].to_numpy(),
    )

    # 경도와 위도 컬럼 생성
    location["경도"] = float("nan")
    location["위도"] = float("nan")

    location.loc[valid, "경도"] = longitude
    location.loc[valid, "위도"] = latitude

    # 변환 결과 저장
    location.to_csv(
        OUTPUT_DIR / "data_location_coordinates.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\n[좌표 변환 완료]")
    print(f"전체 상권 수: {len(location):,}개")
    print(f"좌표 변환 성공: {valid.sum():,}개")

    return location


# ==========================================
# 5. 연도별 매출 데이터와 위치 데이터 결합
# ==========================================

def process_year(year, location):
    file_path = DATA_DIR / f"data_{year}.csv"

    if not file_path.exists():
        print(f"[건너뜀] 파일이 없습니다: {file_path.name}")
        return None

    df = preprocess_data(read_csv_file(file_path))

    if "상권_코드" not in df.columns:
        print(
            f"[확인 필요] {file_path.name}에 "
            "'상권_코드' 컬럼이 없습니다."
        )

        # 상권 코드가 없으면 좌표를 연결할 수 없으므로
        # 전처리 결과만 별도로 저장
        df.to_csv(
            OUTPUT_DIR / f"processed_{year}.csv",
            index=False,
            encoding="utf-8-sig",
        )
        return df

    # 양쪽 파일의 상권 코드를 문자열로 통일
    df["상권_코드"] = (
        df["상권_코드"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    # 매출 데이터에 없는 위치 정보만 추가
    location_columns = [
        "상권_코드",
        "엑스좌표_값",
        "와이좌표_값",
        "경도",
        "위도",
        "자치구_코드_명",
        "행정동_코드_명",
        "영역_면적",
    ]

    available_columns = [
        column
        for column in location_columns
        if column in location.columns
        and (
            column == "상권_코드"
            or column not in df.columns
        )
    ]

    location_for_merge = location[available_columns].copy()

    # 상권 코드를 기준으로 위치 정보 연결
    result = df.merge(
        location_for_merge,
        on="상권_코드",
        how="left",
        validate="many_to_one",
    )

    # 연도 컬럼 추가
    result["분석연도"] = year

    # 결과 저장
    output_path = OUTPUT_DIR / f"processed_{year}.csv"

    result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n[{year}년 처리 완료]")
    print(f"데이터 행 개수: {len(result):,}개")
    print(f"결과 파일: {output_path}")

    if "경도" in result.columns:
        print(
            "위치 정보 연결 성공: "
            f"{result['경도'].notna().sum():,}개 행"
        )

    return result


# ==========================================
# 6. 전체 실행
# ==========================================

def main():
    print("=" * 50)
    print("서울시 상권 데이터 전처리 시작")
    print("=" * 50)

    # 상권 위치 데이터 처리
    location = process_location()

    # 연도별 데이터 처리
    results = []

    for year in [2023, 2024, 2025]:
        result = process_year(year, location)

        if result is not None:
            results.append(result)

    # 연도별 데이터를 하나로 통합
    if results:
        combined = pd.concat(
            results,
            ignore_index=True,
            sort=False,
        )

        combined.to_csv(
            OUTPUT_DIR / "combined_2023_2025.csv",
            index=False,
            encoding="utf-8-sig",
        )

        print("\n[전체 통합 완료]")
        print(f"전체 행 개수: {len(combined):,}개")
        print(
            f"통합 파일: "
            f"{OUTPUT_DIR / 'combined_2023_2025.csv'}"
        )

    print("\n모든 작업이 끝났습니다.")


if __name__ == "__main__":
    main()