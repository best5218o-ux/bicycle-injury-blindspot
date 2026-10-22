"""브랜드 AI — 시군구 단위 확장 분석(228개 시군구). analysis.py(시도 17곳)의 한계를 한 층 더 내려가 점검한다.
실행: python analysis_sgg.py   (입력 data/*.csv, 출력 outputs/results_sgg.json · outputs/sgg_table.csv)
※ 시군구 값은 소수라 우연 변동이 크다 → 사고 규모 하한(부상 합 20명↑)과 부트스트랩 신뢰구간을 함께 쓴다.
※ 생태학적(지역 단위) 상관이며 인과 주장이 아니다. 다중비교 보정 없음(탐색적)."""
import json
import numpy as np
import pandas as pd
from scipy import stats

D = 'data/'
t = pd.read_csv(D + 'bike_injury_by_sgg_2025.csv')
p = pd.read_csv(D + 'population_sgg_2025-12.csv')
w = pd.read_csv(D + 'bike_lane_std_by_sgg.csv')
sido = pd.read_csv(D + 'bike_injury_by_sido_2025.csv')

# ---- 1. 원문 합계 검산: 시군구 합 = 시도 합 = 전국 합 ----
g = t.groupby('sido')[['offender_injured', 'victim_injured']].sum()
s = sido.set_index('sido')
assert (g.offender_injured == s.police_offender_injured.reindex(g.index)).all()
assert (g.victim_injured == s.police_victim_injured.reindex(g.index)).all()
assert t.offender_injured.sum() == 5655 and t.victim_injured.sum() == 8197

d = t.merge(p, on=['sido', 'sgg'], how='left', validate='1:1')
assert d.population.notna().all() and len(d) == 228
d = d.merge(w, on=['sido', 'sgg'], how='left')
d['kind'] = np.where(d.sgg.str.endswith('구'), '구', np.where(d.sgg.str.endswith('시'), '시', '군'))
d.loc[d.sgg == '세종시', 'kind'] = '시'
d['sum_inj'] = d.offender_injured + d.victim_injured
d['rate_off'] = d.offender_injured / d.population * 1e5
d['rate_sum'] = d.sum_inj / d.population * 1e5
d['victim_share'] = d.victim_injured / d.sum_inj.replace(0, np.nan)
d['r70'] = d.population_70plus / d.population * 100
d['gap'] = d.victim_injured - d.offender_injured

rng = np.random.default_rng(0)
def rho(df, a, b):
    df = df[[a, b]].dropna(); n = len(df)
    r0 = stats.spearmanr(df[a], df[b])
    bs = []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        x = stats.spearmanr(df[a].values[i], df[b].values[i]).statistic
        if x == x: bs.append(x)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return dict(n=n, rho=round(float(r0.statistic), 3), p=float('%.3g' % r0.pvalue), ci95=[round(float(lo), 2), round(float(hi), 2)])

res = {}
# ---- 2. 공표(가해 기준) 순위는 '피해 포함' 순위와 얼마나 다른가 ----
res['n_sgg'] = int(len(d))
res['rank_rate_off_vs_rate_sum'] = rho(d, 'rate_off', 'rate_sum')
q_off = d.rate_off >= d.rate_off.quantile(0.75)
q_sum = d.rate_sum >= d.rate_sum.quantile(0.75)
res['top_quartile_overlap'] = dict(n_top_off=int(q_off.sum()), also_top_sum=int((q_off & q_sum).sum()),
                                   dropped_from_top=int((q_off & ~q_sum).sum()), entered_top=int((~q_off & q_sum).sum()))
res['off_zero_or_le2_but_victim_ge10'] = int(((d.offender_injured <= 2) & (d.victim_injured >= 10)).sum())
res['victim_gt_offender'] = int((d.victim_injured > d.offender_injured).sum())
res['victim_ge_2x_offender_among_sum20'] = int(((d.victim_injured >= 2 * d.offender_injured) & (d.sum_inj >= 20)).sum())
res['n_sum20'] = int((d.sum_inj >= 20).sum())

# ---- 3. 피해 몫(피해/(가해+피해))의 지역 구조 : 구·시·군 ----
n20 = d[d.sum_inj >= 20]
res['victim_share_by_kind_sum20'] = {k: dict(n=int(len(v)), median=round(float(v.victim_share.median()), 3)) for k, v in n20.groupby('kind')}
kw = stats.kruskal(*[v.victim_share.values for k, v in n20.groupby('kind')])
res['victim_share_kruskal'] = dict(H=round(float(kw.statistic), 2), p=float('%.3g' % kw.pvalue))
a = n20[n20.kind == '구'].victim_share; b = n20[n20.kind != '구'].victim_share
mu = stats.mannwhitneyu(a, b, alternative='two-sided')
res['victim_share_gu_vs_rest'] = dict(median_gu=round(float(a.median()), 3), median_rest=round(float(b.median()), 3), p=float('%.3g' % mu.pvalue))
res['victim_share_vs_70plus'] = rho(n20, 'victim_share', 'r70')
res['rate_off_vs_70plus'] = rho(d, 'rate_off', 'r70')
res['rate_sum_vs_70plus'] = rho(d, 'rate_sum', 'r70')

# ---- 4. 자전거도로 폭(표준데이터)과의 대응 : 폭이 기록된 겸용도로 km ≥ 5 인 시군구 ----
d['share_lt2'] = (d['km_w_lt1.5'] + d['km_w_1.5_2']) / d.km_shared_width_known.replace(0, np.nan) * 100
wk = d[(d.km_shared_width_known >= 5) & (d.sum_inj >= 10)]
res['width_subset_n'] = int(len(wk))
res['width_vs_rate_sum'] = rho(wk, 'share_lt2', 'rate_sum')
res['width_vs_victim_share'] = rho(wk, 'share_lt2', 'victim_share')
res['width_vs_rate_off'] = rho(wk, 'share_lt2', 'rate_off')
res['std_coverage'] = dict(n_with_std=int(d.km_total.notna().sum()), n_width_ge5km=int((d.km_shared_width_known >= 5).sum()),
                           km_shared_width_known=round(float(d.km_shared_width_known.sum()), 1),
                           km_lt2=round(float(d[['km_w_lt1.5', 'km_w_1.5_2']].sum().sum()), 1))
res['std_coverage']['share_lt2_national_pct'] = round(res['std_coverage']['km_lt2'] / res['std_coverage']['km_shared_width_known'] * 100, 1)

# ---- 5. 구체 사례 : 공표엔 거의 없는데 피해는 큰 시군구 ----
top = d[d.sum_inj >= 20].assign(r=lambda x: x.victim_injured / x.offender_injured.replace(0, np.nan)).sort_values('gap', ascending=False)
res['top_gap'] = [dict(sido=r.sido, sgg=r.sgg, off=int(r.offender_injured), vic=int(r.victim_injured)) for r in top.head(10).itertuples()]
ex = d[(d.victim_injured >= 15)].assign(r=lambda x: x.victim_injured / x.offender_injured.clip(lower=1)).sort_values('r', ascending=False)
res['top_ratio_vic15'] = [dict(sido=r.sido, sgg=r.sgg, off=int(r.offender_injured), vic=int(r.victim_injured)) for r in ex.head(8).itertuples()]

json.dump(res, open('outputs/results_sgg.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
d.drop(columns=['n_segments']).round(3).to_csv('outputs/sgg_table.csv', index=False, encoding='utf-8-sig')
print(json.dumps(res, ensure_ascii=False, indent=1))
