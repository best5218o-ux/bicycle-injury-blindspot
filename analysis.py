"""브랜드 AI — 통계에 잡히지 않는 자전거 부상: 재현 코드.
실행: pip install -r requirements.txt && python analysis.py && python make_figures.py
입력은 data/*.csv 뿐이며(출처는 data/SOURCES.md), 모든 합계를 원문 값과 대조(assert)한 뒤 통계를 계산한다."""
import json
import numpy as np
import pandas as pd
from scipy import stats

DATA = 'data/'
MET = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']   # 서울·광역시(세종 제외)

r = pd.read_csv(DATA + 'bike_injury_by_sido_2025.csv')
r = r.merge(pd.read_csv(DATA + 'population_2025-12.csv'), on='sido')
r = r.merge(pd.read_csv(DATA + 'bike_lane_km_by_sido_2025.csv'), on='sido')
ts = pd.read_csv(DATA + 'bike_lane_km_timeseries_2011_2025.csv')

# ---- 1. 원문 합계 검산 ----
assert len(r) == 17
assert r.police_offender_injured.sum() == 5655        # 통계집 쪽 32 합계
assert r.police_victim_injured.sum() == 8197          # TAAS 합계 = 통계집 쪽 27 피해 부상 계
assert r.nfa119_bike_transported.sum() == 20503       # 119 연보 21) 합계
assert abs(r.lane_km_total.sum() - 28453.41) < 0.01 and abs(r.lane_km_shared.sum() - 21033.32) < 0.01
assert (ts.total_km - ts.shared_km - ts.dedicated_km - ts.other_km).abs().max() == 0
assert (r.nfa119_bike_transported == r.nfa119_bike_transported.astype(int)).all()
POLICE_ALL_NATIONAL = 13085                           # 통계집 쪽 26 (자전거 대 자전거 중복 제외)

# ---- 2. 전국 3층 비교 ----
nat = dict(published=5655, police_all=POLICE_ALL_NATIONAL, nfa119=20503,
           victim=8197, overlap=5655 + 8197 - POLICE_ALL_NATIONAL)
nat['published_share_of_119'] = nat['published'] / nat['nfa119']
nat['police_all_share_of_119'] = nat['police_all'] / nat['nfa119']
nat['ratio_119_to_published'] = nat['nfa119'] / nat['published']
nat['ratio_119_to_police_all'] = nat['nfa119'] / nat['police_all']
nat['victim_share_of_sum'] = 8197 / (5655 + 8197)

# ---- 3. 시도 지표 ----
r['police_sum'] = r.police_offender_injured + r.police_victim_injured          # 이중집계 포함 상한
r['ratio_pub'] = r.nfa119_bike_transported / r.police_offender_injured        # 119 ÷ 공표(가해)
r['ratio_all'] = r.nfa119_bike_transported / r.police_sum                     # 119 ÷ 경찰 전체(상한)
r['victim_share'] = r.police_victim_injured / r.police_sum
r['r70'] = r.population_70plus / r.population * 100
r['rate_pub'] = r.police_offender_injured / r.population * 1e5
r['rate_all'] = r.police_sum / r.population * 1e5
r['rate_119'] = r.nfa119_bike_transported / r.population * 1e5
r['shared_pct'] = r.lane_km_shared / r.lane_km_total * 100
for c in ['rate_pub', 'rate_all', 'rate_119']:
    r['rank_' + c] = r[c].rank(ascending=False).astype(int)
r['metro'] = r.sido.isin(MET).astype(int)

def rho(a, b):
    s = stats.spearmanr(r[a], r[b]);  return dict(rho=round(float(s.statistic), 3), p=float('%.3g' % s.pvalue))
def mwu(col):
    g1, g0 = r[r.metro == 0][col], r[r.metro == 1][col]
    u = stats.mannwhitneyu(g1, g0, alternative='two-sided')
    return dict(p=round(float(u.pvalue), 4), median_nonmetro=round(float(g1.median()), 2), median_metro=round(float(g0.median()), 2))

res = dict(national=nat,
    metro_vs_other=dict(n_metro=int(r.metro.sum()), n_other=int((1 - r.metro).sum()),
        ratio_pub=mwu('ratio_pub'), ratio_all=mwu('ratio_all'), victim_share=mwu('victim_share')),
    spearman=dict(ratio_pub_vs_victim_share=rho('ratio_pub', 'victim_share'),
        pct70_vs_rate_pub=rho('r70', 'rate_pub'), pct70_vs_rate_all=rho('r70', 'rate_all'), pct70_vs_rate_119=rho('r70', 'rate_119'),
        rate_pub_vs_rate_119=rho('rate_pub', 'rate_119'), rate_all_vs_rate_119=rho('rate_all', 'rate_119'),
        shared_pct_vs_rate_119=rho('shared_pct', 'rate_119'), shared_pct_vs_rate_all=rho('shared_pct', 'rate_all'),
        metro_vs_ratio_pub=rho('metro', 'ratio_pub'), metro_vs_ratio_all=rho('metro', 'ratio_all')),
    facility=dict(shared_pct_2011=float(ts.shared_km.iloc[0] / ts.total_km.iloc[0] * 100),
        shared_pct_2015=float(ts.shared_km.iloc[4] / ts.total_km.iloc[4] * 100),
        shared_pct_2025=float(ts.shared_km.iloc[-1] / ts.total_km.iloc[-1] * 100),
        total_growth=float(ts.total_km.iloc[-1] / ts.total_km.iloc[0]),
        shared_share_of_growth=float((ts.shared_km.iloc[-1] - ts.shared_km.iloc[0]) / (ts.total_km.iloc[-1] - ts.total_km.iloc[0]))))
# ---- 4. 통계집의 세부 표(전국) : 단독사고·연령 ----
# 통계집 쪽 28 「2-1 가해자사고 사고유형별」: 자전거 단독 부상 197 (가해 부상 5,655 중)
# 통계집 쪽 29 「2-2 연령별」: 65세 이상 부상 가해 1,380 / 피해 2,393, 사망 가해 55/85 · 피해 80/106
DET = dict(single_bike_injured=197, offender_injured=5655, inj65_offender=1380, inj65_victim=2393,
           death65_offender=55, death_offender=85, death65_victim=80, death_victim=106)
DET['single_share_of_offender'] = DET['single_bike_injured'] / DET['offender_injured']
DET['inj65_victim_to_offender'] = DET['inj65_victim'] / DET['inj65_offender']
DET['death65_victim_share'] = DET['death65_victim'] / DET['death_victim']
res['police_detail'] = DET
# ---- 5. 연도별 추세(2021~2025): 틈은 해마다 반복되는가 ----
tsr = pd.read_csv(DATA + 'bike_injury_timeseries_2021_2025.csv')
assert tsr.set_index('year').loc[2025].tolist() == [5655, 13085, 20503, 153308]
tsr['pub_share_of_119'] = tsr.police_offender_injured / tsr.nfa119_bike_transported
tsr['all_share_of_119'] = tsr.police_all_injured / tsr.nfa119_bike_transported
tsr['bike_share_of_119_traffic'] = tsr.nfa119_bike_transported / tsr.nfa119_traffic_total
res['trend'] = {int(y): dict(pub_share=round(float(a), 3), all_share=round(float(b), 3), bike_share_traffic=round(float(c), 3))
                for y, a, b, c in zip(tsr.year, tsr.pub_share_of_119, tsr.all_share_of_119, tsr.bike_share_of_119_traffic)}
# ---- 6. 도·광역시 배수 차이의 분해: 119÷공표 = (119÷경찰 전체) × 1/(1−피해 비중) — 곱이므로 로그로 나눈다(기하평균) ----
gm = lambda s: float(np.exp(np.log(s).mean()))
o, mt = r[r.metro == 0], r[r.metro == 1]
L_pub = np.log(gm(o.ratio_pub) / gm(mt.ratio_pub)); L_all = np.log(gm(o.ratio_all) / gm(mt.ratio_all))
res['decomposition'] = dict(gm_ratio_pub_nonmetro=round(gm(o.ratio_pub), 2), gm_ratio_pub_metro=round(gm(mt.ratio_pub), 2),
    share_from_victim_basis=round(float(1 - L_all / L_pub), 3), share_from_police_119_gap=round(float(L_all / L_pub), 3))
res['spearman']['ratio_all_vs_victim_share'] = rho('ratio_all', 'victim_share')
r.to_csv('outputs/region_table.csv', index=False)
json.dump(res, open('outputs/results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print(r[['sido', 'ratio_pub', 'ratio_all', 'victim_share', 'rank_rate_pub', 'rank_rate_all', 'rank_rate_119']].round(2).to_string(index=False))
