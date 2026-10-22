# 통계에 잡히지 않는 자전거 부상 (팀 브랜드 AI)
AI와 함께하는 교통문제 해결을 위한 데이터 분석 공모전 제출 분석코드.

```
pip install -r requirements.txt
python analysis.py        # 원문 합계 검산(assert) → outputs/results.json, outputs/region_table.csv
python analysis_sgg.py    # 시군구 228곳 확장 분석 → outputs/results_sgg.json, sgg_table.csv
python make_figures.py    # figures/fig1~fig6
```
- data/ : 시도별 공표(가해자 기준)·피해운전자·119 이송 부상, 인구, 자전거도로 연장 (출처: data/SOURCES.md)
- analysis.py : 합계 검산 + 3층 비교, 피해 비중, 119÷공표, 119÷경찰전체, Spearman, Mann-Whitney U
- 모든 입력은 공개 통계이며 개인정보가 없다.
- analysis_sgg.py : 시군구 단위(합계 검산 → 순위 변화, 피해 몫의 구·시·군 차이, 부트스트랩 CI, 자전거도로 폭 대응)
- aggregate_bike_lanes.py : 표준데이터 원자료 → 시군구 폭 집계(참고 구현, 검증 기준값 주석)

검증 환경: Python 3.12, pandas 3.0.6, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2 에서 새 가상환경으로 처음부터 실행해 결과(outputs/*.json)가 동일함을 확인(2026-10-22). 부트스트랩은 시드 고정(0)이라 같은 값이 나온다.

주요 결과: 공표(가해자 기준) 자전거 부상 5,655명 = 119 이송 20,503명의 28% · 경찰 전체 13,085명 = 64% · 피해운전자 몫 59% · 시군구 228곳 피해 몫 중앙값 구 56% / 시 62% / 군 67%.
