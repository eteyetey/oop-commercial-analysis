import numpy as np
import pandas as pd
import plotly.graph_objects as go

class PlotlyVisualizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_3d_gaussian_surface(self, sigma=0.01, grid_size=80):
        """3D 가우스 매출 산맥 생성"""
        if self.df.empty:
            return go.Figure()

        x_lon = self.df['경도'].values
        y_lat = self.df['위도'].values
        sales = self.df['매출금액'].values

        # 2D 격자 생성
        x_range = np.linspace(x_lon.min() - 0.01, x_lon.max() + 0.01, grid_size)
        y_range = np.linspace(y_lat.min() - 0.01, y_lat.max() + 0.01, grid_size)
        X, Y = np.meshgrid(x_range, y_range)

        # 3D 높이(Z) 계산
        Z = np.zeros_like(X)
        for x_i, y_i, w_i in zip(x_lon, y_lat, sales):
            dist_sq = (X - x_i)**2 + (Y - y_i)**2
            Z += w_i * np.exp(-dist_sq / (2 * sigma**2))

        # Plotly Surface 반환
        fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Hot')])
        fig.update_layout(
            title="3D 가우스 매출 산맥",
            scene=dict(xaxis_title="경도", yaxis_title="위도", zaxis_title="매출 밀도"),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig