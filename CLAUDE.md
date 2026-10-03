# CLAUDE.md

이 파일은 Claude가 이 레포에서 작업할 때 **항상** 따라야 하는 지침입니다.
아래 "작업 양식 / 규칙" 섹션이 최우선이며, 나머지는 프로젝트 참고 정보입니다.

---

## 📌 작업 양식 / 규칙 (사용자 작성)

<!-- 여기에 원하는 양식과 규칙을 적어주세요. Claude는 모든 작업에서 이 내용을 따릅니다. -->



---

## 프로젝트 개요

광운대학교 2026-2 객체지향프로그래밍(01) 팀 프로젝트.
상권 매출 데이터를 Streamlit 대시보드에서 3D로 시각화한다 (Plotly 가우스 표면 + Pydeck 기둥 지도).

## 실행
run이라고 작성시 밑의 코드를 terminal 에서 실행한다.

```
conda env create -f environment.yml   # 환경 이름: project_env (Python 3.11)
conda activate project_env
streamlit run app.py
```

## 구조 (역할별 클래스 분리)

| 파일 | 클래스 | 역할 |
|---|---|---|
| [app.py](app.py) | — | Streamlit 진입점. 사이드바 필터(연도/분기), 지표 카드, 시각화 배치 |
| [data_loader.py](data_loader.py) | `DataLoader` | CSV 로드 및 전처리 (`load_and_preprocess`) |
| [filter_analyzer.py](filter_analyzer.py) | `DataFilter`, `DataAnalyzer` | 연도/분기/상권코드 필터링, 요약 통계(총매출·총건수·평균객단가) |
| [viz_plotly.py](viz_plotly.py) | `PlotlyVisualizer` | 3D 가우스 매출 산맥 (`create_3d_gaussian_surface`) |
| [viz_pydeck.py](viz_pydeck.py) | `PydeckVisualizer` | 3D 기둥 지도 (`create_column_map`) |
| [data.csv](data.csv) | — | 샘플 데이터 |

데이터 흐름: `DataLoader` → `DataFilter` → `DataAnalyzer` / `PlotlyVisualizer` / `PydeckVisualizer` → `app.py`에서 렌더링

## 데이터 컬럼 (data.csv)

`연도, 분기, 상권코드, 상권명, 위도, 경도, 매출금액, 매출건수` — 컬럼명은 한글이며 코드에서 그대로 사용한다.

## 기존 코드 컨벤션

- 기능별로 클래스 하나씩, 생성자에서 `DataFrame`을 받아 `self.df`에 보관
- 타입 힌트 사용 (`df: pd.DataFrame`, `-> pd.DataFrame`, `-> dict`)
- 주석·docstring은 한국어
- 각 모듈은 팀원별 담당 영역 (전처리 / 분석·필터 / Plotly / Pydeck / Streamlit)
