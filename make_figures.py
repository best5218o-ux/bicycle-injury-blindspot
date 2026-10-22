"""그림 1~6 생성. 먼저 python analysis.py 와 python analysis_sgg.py 를 실행해 outputs/ 를 만든다."""
import glob, json
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

for f in glob.glob('/usr/share/fonts/**/*CJK*.ttc', recursive=True) + glob.glob('/usr/share/fonts/**/Nanum*.ttf', recursive=True):
    fm.fontManager.addfont(f)
names = {f.name for f in fm.fontManager.ttflist}
plt.rcParams['font.family'] = next((n for n in ['Noto Sans CJK KR', 'NanumGothic', 'Malgun Gothic', 'AppleGothic'] if n in names), 'sans-serif')
plt.rcParams.update({'axes.unicode_minus': False, 'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 11})
GREY, BLUE, RED, INK = '#9AA3AD', '#4F7CAC', '#D9482B', '#1F2933'
d = pd.read_csv('outputs/region_table.csv'); R = json.load(open('outputs/results.json', encoding='utf-8'))
ts = pd.read_csv('data/bike_lane_km_timeseries_2011_2025.csv')
comma = FuncFormatter(lambda x, _: f'{int(x):,}')
N = R['national']

# 그림 1: 세 집계
fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=200)
off, vic_only = N['published'], N['police_all'] - N['published']
ax.bar(0, off, color=GREY, width=.55)
ax.bar(1, off, color=GREY, width=.55); ax.bar(1, vic_only, bottom=off, color=BLUE, width=.55)
ax.bar(2, N['nfa119'], color=RED, width=.55)
ax.text(0, off + 350, f"{off:,}명\n(119의 {N['published_share_of_119']:.0%})", ha='center', fontweight='bold', color=INK, fontsize=10)
ax.text(1, N['police_all'] + 350, f"{N['police_all']:,}명\n(119의 {N['police_all_share_of_119']:.0%})", ha='center', fontweight='bold', color=INK, fontsize=10)
ax.text(2, N['nfa119'] + 350, f"{N['nfa119']:,}명\n(기준 100%)", ha='center', fontweight='bold', color=INK, fontsize=10)
ax.text(1, off + vic_only / 2, '피해운전자\n(공표에서 빠짐)', ha='center', va='center', color='white', fontsize=9)
ax.text(1, off / 2, '가해운전자', ha='center', va='center', color='white', fontsize=9)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['① 공표 통계\n(행안부, 가해자 기준)', '② 경찰DB 전체\n(가해+피해, 중복 제외)', '③ 119 구급\n이송환자'])
ax.set_ylim(0, 25500); ax.yaxis.set_major_formatter(comma); ax.set_ylabel('2025년 자전거 부상·이송 (명)')
ax.set_title('같은 해 자전거 부상, 세 가지 공식 집계', loc='left', fontweight='bold')
plt.tight_layout(); plt.savefig('figures/fig1_three_counts.png'); plt.close()

# 그림 2: 피해 비중
s = d.sort_values('victim_share'); met = s.metro == 1
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
ax.barh(s.sido, s.victim_share * 100, color=[BLUE if m else RED for m in met], height=.7)
for y, v in enumerate(s.victim_share * 100): ax.text(v + .8, y, f'{v:.0f}%', va='center', fontsize=9.5)
ax.axvline(N['victim_share_of_sum'] * 100, color=INK, ls='--', lw=1); ax.text(N['victim_share_of_sum'] * 100 + .6, -0.9, '전국 59%', fontsize=9, color=INK)
ax.set_xlim(0, 88); ax.set_xlabel('경찰 자전거 부상(가해+피해) 중 피해운전자 몫 (%)')
ax.set_title('가해자 기준이 가리는 몫: 서울 47% → 전북 76%', loc='left', fontweight='bold')
ax.legend(handles=[Patch(color=RED, label='도·세종'), Patch(color=BLUE, label='서울·광역시')], loc='lower right', frameon=False)
plt.tight_layout(); plt.savefig('figures/fig2_victim_share.png'); plt.close()

# 그림 3: 119 ÷ 경찰 전체
s = d.sort_values('ratio_all'); met = s.metro == 1
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
ax.barh(s.sido, s.ratio_all, color=[BLUE if m else RED for m in met], height=.7)
for y, v in enumerate(s.ratio_all): ax.text(v + .03, y, f'{v:.1f}배', va='center', fontsize=9.5, bbox=dict(fc='white', ec='none', pad=.5), zorder=5)
ax.axvline(1, color=INK, lw=1); ax.text(1.02, -0.95, '119=경찰 전체', fontsize=8.5)
ax.set_xlim(0, 3.1); ax.set_xlabel('119 자전거 이송 ÷ 경찰 전체 자전거 부상(가해+피해 단순 합, 상한)')
ax.set_title('경찰 전체로 맞춰도 119가 더 많다 — 농촌에서 더 크다', loc='left', fontweight='bold', fontsize=11.5)
ax.legend(handles=[Patch(color=RED, label=f"도·세종 (중앙값 {R['metro_vs_other']['ratio_all']['median_nonmetro']:.1f}배)"), Patch(color=BLUE, label=f"서울·광역시 (중앙값 {R['metro_vs_other']['ratio_all']['median_metro']:.1f}배)")], loc='lower right', frameon=False)
plt.tight_layout(); plt.savefig('figures/fig3_ratio_all.png'); plt.close()

# 그림 4: 순위 3열
cols = [('rank_rate_pub', '공표 통계\n(가해자 기준)'), ('rank_rate_all', '경찰 전체\n(가해+피해)'), ('rank_rate_119', '119 이송')]
hl = {'전북': RED, '경북': RED, '서울': BLUE}
fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)
for _, r in d.iterrows():
    c = hl.get(r.sido, '#C9CED4'); lw = 2.4 if r.sido in hl else 1; z = 3 if r.sido in hl else 2
    for i in range(2): ax.plot([i, i + 1], [r[cols[i][0]], r[cols[i + 1][0]]], color=c, lw=lw, zorder=z)
    tc = c if r.sido in hl else '#59636E'; fw = 'bold' if r.sido in hl else 'normal'
    ax.text(-.05, r[cols[0][0]], f'{r.sido} {int(r[cols[0][0]])}', ha='right', va='center', fontsize=9.5, color=tc, fontweight=fw)
    ax.text(1, r[cols[1][0]] - .0, '', fontsize=1)
    ax.text(2.05, r[cols[2][0]], f'{int(r[cols[2][0]])} {r.sido}', ha='left', va='center', fontsize=9.5, color=tc, fontweight=fw)
    if r.sido in hl: ax.text(1, r[cols[1][0]] - .45, f'{int(r[cols[1][0]])}위', ha='center', fontsize=9, color=c, fontweight='bold')
for i, (_, t) in enumerate(cols): ax.text(i, -0.2, t, ha='center', va='bottom', fontweight='bold', fontsize=10)
ax.set_ylim(17.8, -1.6); ax.set_xlim(-.6, 2.6); ax.axis('off')
plt.tight_layout(); plt.savefig('figures/fig4_rank_slope.png'); plt.close()

# 그림 5: 시설
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
ax.stackplot(ts.year, ts.dedicated_km, ts.shared_km, ts.other_km, colors=[BLUE, RED, '#C9CED4'], labels=['전용도로', '겸용도로 (보행자와 공유)', '전용차로·우선도로'])
ax.set_ylabel('자전거도로 연장 (km)'); ax.yaxis.set_major_formatter(comma); ax.legend(loc='upper left', frameon=False, fontsize=9)
F = R['facility']
ax.text(2025, ts.total_km.iloc[-1] + 500, f"28,453km\n겸용 {F['shared_pct_2025']:.0f}%", ha='right', fontweight='bold', fontsize=9.5)
ax.text(2011, ts.total_km.iloc[0] + 500, f"15,307km\n겸용 {F['shared_pct_2011']:.0f}%", ha='left', fontweight='bold', fontsize=9.5)
ax.set_ylim(0, 34000); ax.set_xlim(2011, 2025)
ax.set_title('15년간 1.9배 늘었지만 4분의 3은 보행자와 나눠 쓰는 길', loc='left', fontweight='bold', fontsize=11.5)
plt.tight_layout(); plt.savefig('figures/fig5_lane_composition.png'); plt.close()

# 그림 6: 시군구(228곳)
import numpy as np
S = pd.read_csv('outputs/sgg_table.csv'); RS = json.load(open('outputs/results_sgg.json', encoding='utf-8'))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 4.3), dpi=200, gridspec_kw={'width_ratios': [1, 1.25]})
n20 = S[S.sum_inj >= 20]; rng = np.random.default_rng(1)
for i, (k, c) in enumerate([('구', BLUE), ('시', GREY), ('군', RED)]):
    v = n20[n20.kind == k].victim_share * 100
    a1.scatter(i + rng.uniform(-.17, .17, len(v)), v, s=14, color=c, alpha=.75, lw=0)
    a1.hlines(v.median(), i - .3, i + .3, color=INK, lw=2)
    a1.text(i, 112, f'중앙값 {v.median():.0f}%\n(n={len(v)})', ha='center', va='top', fontsize=8.5, color=INK, fontweight='bold')
a1.set_xticks([0, 1, 2]); a1.set_xticklabels(['구', '시', '군']); a1.set_ylim(0, 114); a1.set_yticks([0, 20, 40, 60, 80, 100]); a1.set_ylabel('피해운전자 몫 (%)')
a1.set_title('피해 몫: 군 > 시 > 구', loc='left', fontweight='bold', fontsize=10.5)
t8 = RS['top_ratio_vic15'][:8][::-1]
y = np.arange(len(t8))
a2.barh(y + .2, [r['vic'] for r in t8], height=.38, color=BLUE, label='피해운전자 부상(경찰DB)')
a2.barh(y - .2, [r['off'] for r in t8], height=.38, color=GREY, label='공표 기준(가해운전자 부상)')
a2.set_yticks(y); a2.set_yticklabels([f"{r['sido']} {r['sgg']}" for r in t8], fontsize=9)
for yi, r in zip(y, t8):
    a2.text(r['vic'] + 1, yi + .2, str(r['vic']), va='center', fontsize=8.5); a2.text(r['off'] + 1, yi - .2, str(r['off']), va='center', fontsize=8.5)
a2.legend(frameon=False, fontsize=8, loc='lower right'); a2.set_xlim(0, 75)
a2.set_title('공표 대비 피해가 큰 시군구', loc='left', fontweight='bold', fontsize=10.5)
plt.tight_layout(); plt.savefig('figures/fig6_sgg.png'); plt.close()
print('figures ok')
