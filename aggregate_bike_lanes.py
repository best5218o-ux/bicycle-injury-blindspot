"""전국자전거도로표준데이터(공공데이터포털 15100063) 원자료 → 시군구별 폭 집계(data/bike_lane_std_by_sgg.csv).
입력: 포털의 표준데이터 행 전체를 CSV로 저장한 파일(열 이름은 표준 영문 열: CTPV_NM, SGG_NM, RTE_NM, ROAD_ST_POINT_LAT/LON,
ROAD_ED_POINT_LAT, TOTAL_LENGTH(km), BIKE_ROAD_TYPE, BIKE_ROAD_WIDTH(m)). 실행: python aggregate_bike_lanes.py raw.csv
2025-10-22 확인값(검증 기준): 원자료 20,474행 → 중복 304행 제거 → 20,170행, 전국 합계 km_total≈18,052, 유형 기재 12,651km,
겸용 9,656km 중 폭 기재 9,496km, 그중 2m 미만 3,564km(37.5%).
※ 이 파일은 표준데이터에 등록된 구간만 담는다(통계집 28,453km 대비 63%, 세종 없음, 울산은 유형 미기재). 완전한 전수가 아니다."""
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1], dtype=str)
key = ['CTPV_NM', 'SGG_NM', 'RTE_NM', 'ROAD_ST_POINT_LAT', 'ROAD_ST_POINT_LON', 'ROAD_ED_POINT_LAT', 'TOTAL_LENGTH']
n0 = len(df); df = df.drop_duplicates(subset=key); print('중복 제거', n0, '->', len(df))
df['L'] = pd.to_numeric(df.TOTAL_LENGTH, errors='coerce').fillna(0)
df['W'] = pd.to_numeric(df.BIKE_ROAD_WIDTH, errors='coerce')
t = df.BIKE_ROAD_TYPE.fillna('')
df['typed'] = t != ''; df['shared'] = t.str.contains('겸용'); df['wk'] = df.shared & (df.W > 0)
SIDO = {'서울특별시': '서울', '부산광역시': '부산', '대구광역시': '대구', '인천광역시': '인천', '광주광역시': '광주', '대전광역시': '대전', '울산광역시': '울산',
        '세종특별자치시': '세종', '경기도': '경기', '강원도': '강원', '강원특별자치도': '강원', '충청북도': '충북', '충청남도': '충남', '전라북도': '전북',
        '전북특별자치도': '전북', '전라남도': '전남', '경상북도': '경북', '경상남도': '경남', '제주특별자치도': '제주'}
GJ = {'동구', '서구', '남구', '북구', '광산구'}
def sido(r):
    if r.CTPV_NM == '전남광주통합특별시': return '광주' if r.SGG_NM in GJ else '전남'   # 2026 행정구역 통합 표기 → 2025 시도로 환원
    return SIDO.get(r.CTPV_NM, r.CTPV_NM)
df['sido'] = df.apply(sido, axis=1)
def agg(g):
    L = g.L; w = g.W
    return pd.Series({'n_segments': len(g), 'km_total': L.sum(), 'km_typed': L[g.typed].sum(), 'km_shared': L[g.shared].sum(),
        'km_shared_width_known': L[g.wk].sum(), 'km_w_lt1.5': L[g.wk & (w < 1.5)].sum(), 'km_w_1.5_2': L[g.wk & (w >= 1.5) & (w < 2)].sum(),
        'km_w_2_3': L[g.wk & (w >= 2) & (w < 3)].sum(), 'km_w_ge3': L[g.wk & (w >= 3)].sum()})
out = df.groupby(['sido', 'SGG_NM']).apply(agg).reset_index().rename(columns={'SGG_NM': 'sgg'}).round(1)
out.to_csv('data/bike_lane_std_by_sgg.csv', index=False, encoding='utf-8')
print(out[['km_total', 'km_typed', 'km_shared', 'km_shared_width_known']].sum().round(0).to_dict())
