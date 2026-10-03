import pandas as pd

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_data = None

    def load_and_preprocess(self) -> pd.DataFrame:
        """데이터 로드 및 기본 전처리 수행"""
        # 1. 파일 읽기
        df = pd.read_csv(self.file_path)
        
        # 2. 전처리 로직 (결측치 처리, 데이터 타입 변환 등)
        df['연도'] = df['연도'].astype(int)
        df['분기'] = df['분기'].astype(int)
        df['매출금액'] = df['매출금액'].fillna(0)
        
        self.raw_data = df
        return self.raw_data