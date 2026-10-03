import pandas as pd

class DataFilter:
    """필터링 전담 클래스"""
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def apply_filters(self, year: int, quarter: int, district_code: str = None) -> pd.DataFrame:
        filtered_df = self.df[(self.df['연도'] == year) & (self.df['분기'] == quarter)]
        if district_code and district_code != "전체":
            filtered_df = filtered_df[filtered_df['상권코드'] == district_code]
        return filtered_df


class DataAnalyzer:
    """통계 분석 전담 클래스"""
    def __init__(self, filtered_df: pd.DataFrame):
        self.df = filtered_df

    def get_summary_stats(self) -> dict:
        """기본 통계 지표 산출"""
        total_sales = self.df['매출금액'].sum()
        total_count = self.df['매출건수'].sum()
        avg_price = total_sales / total_count if total_count > 0 else 0
        return {
            "총매출": total_sales,
            "총건수": total_count,
            "평균객단가": avg_price
        }