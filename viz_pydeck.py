import pydeck as pdk
import pandas as pd

class PydeckVisualizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_column_map(self):
        """Pydeck 3D 기둥 지도 생성"""
        layer = pdk.Layer(
            "ColumnLayer",
            self.df,
            get_position=["경도", "위도"],
            get_elevation="매출금액",
            elevation_scale=0.1,
            radius=50,
            get_fill_color="[255, 140, 0, 200]",
            pickable=True,
        )
        
        view_state = pdk.ViewState(
            longitude=self.df['경도'].mean() if not self.df.empty else 126.97,
            latitude=self.df['위도'].mean() if not self.df.empty else 37.56,
            zoom=12,
            pitch=45,
        )
        return pdk.Deck(layers=[layer], initial_view_state=view_state)