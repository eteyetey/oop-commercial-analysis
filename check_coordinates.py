
import pandas as pd
from pathlib import Path

file_path = Path("output/data_location_coordinates.csv")

df = pd.read_csv(file_path, encoding="utf-8-sig")

print("전체 상권 수:", len(df))
print("경도 누락:", df["경도"].isna().sum())
print("위도 누락:", df["위도"].isna().sum())

# 서울 주변의 대략적인 범위를 기준으로 확인
invalid = df[
    ~df["경도"].between(126.7, 127.3)
    | ~df["위도"].between(37.3, 37.8)
]

print("서울 주변 범위를 벗어난 좌표:", len(invalid))

if len(invalid) > 0:
    print(invalid[["상권_코드_명", "경도", "위도"]].head(20))
else:
    print("좌표 범위 검사 완료")