"""그림 1·2·4·5 생성(그림 3 지도는 make_maps.py). 먼저 python analysis.py 와 python analysis_sgg.py 를 실행해 outputs/ 를 만든다."""
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

# 그림 1: (가) 2025년 세 집계 (나) 2021~2025년 추세
tr = pd.read_csv('data/bike_injury_timeseries_2021_2025.csv')
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.6, 3.7), dpi=220, gridspec_kw={'width_ratios': [1.15, 1]})
off, vic_only = N['published'], N['police_all'] - N['published']
ax.bar(0, off, color=GREY, width=.6); ax.bar(1, off, color=GREY, width=.6); ax.bar(1, vic_only, bottom=off, color=BLUE, width=.6)
ax.bar(2, N['nfa119'], color=RED, width=.6)
for x, v, t in [(0, off, f"{off:,}명\n(119의 {N['published_share_of_119']:.0%})"), (1, N['police_all'], f"{N['police_all']:,}명\n(119의 {N['police_all_share_of_119']:.0%})"), (2, N['nfa119'], f"{N['nfa119']:,}명")]:
    ax.text(x, v + 400, t, ha='center', fontweight='bold', color=INK, fontsize=8.5)
ax.text(1, off + vic_only / 2, '피해운전자', ha='center', va='center', color='white', fontsize=8)
ax.text(1, off / 2, '가해운전자', ha='center', va='center', color='white', fontsize=8)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['① 공표 통계\n(가해자 기준)', '② 경찰 전체\n(가해+피해)', '③ 119 구급\n이송'], fontsize=8.5)
ax.set_ylim(0, 25500); ax.yaxis.set_major_formatter(comma); ax.tick_params(axis='y', labelsize=8)
ax.set_title('(가) 2025년 자전거 부상·이송', loc='left', fontweight='bold', fontsize=10)
for col, c, lab in [('nfa119_bike_transported', RED, '119 구급 이송'), ('police_all_injured', BLUE, '경찰 전체(가해+피해)'), ('police_offender_injured', GREY, '공표(가해자 기준)')]:
    bx.plot(tr.year, tr[col], marker='o', ms=4, color=c, lw=2)
    bx.text(2025.15, tr[col].iloc[-1], f"{lab}\n{tr[col].iloc[-1]:,}", va='center', fontsize=7.8, color=c, fontweight='bold')
for y, a, b in zip(tr.year, tr.police_offender_injured, tr.nfa119_bike_transported):
    bx.text(y, a - 2300, f'{a / b:.0%}', ha='center', fontsize=7.5, color='#59636E')
bx.text(2020.7, 1100, '공표÷119 비율', fontsize=7.5, color='#59636E', ha='left')
bx.set_xlim(2020.6, 2027.2); bx.set_ylim(0, 25500); bx.set_xticks(list(tr.year)); bx.tick_params(labelsize=8)
bx.yaxis.set_major_formatter(comma); bx.spines['left'].set_visible(False); bx.set_yticks([])
bx.set_title('(나) 2021~2025년: 해마다 26~28%만 공표', loc='left', fontweight='bold', fontsize=10)
plt.tight_layout(); plt.savefig('figures/fig1_three_counts.png'); plt.close()

# 그림 2: 공표가 놓치는 두 층 — (가) 피해운전자 비중 (나) 119 ÷ 경찰 전체
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.6, 4.4), dpi=220, sharey=False)
s = d.sort_values('victim_share'); met = s.metro == 1
ax.barh(s.sido, s.victim_share * 100, color=[BLUE if m else RED for m in met], height=.72)
for y, v in enumerate(s.victim_share * 100): ax.text(v + 1, y, f'{v:.0f}%', va='center', fontsize=7.8, bbox=dict(fc='white', ec='none', pad=.3), zorder=5)
ax.axvline(N['victim_share_of_sum'] * 100, color=INK, ls='--', lw=.9); ax.text(N['victim_share_of_sum'] * 100 - 1, 17.1, '전국 59%', fontsize=7.8, color=INK, ha='right')
ax.set_xlim(0, 90); ax.set_ylim(-0.7, 17.6); ax.tick_params(labelsize=8)
ax.set_xlabel('경찰 부상(가해+피해 단순 합) 중 피해운전자 비중(%)', fontsize=8)
ax.set_title('(가) 공표에서 빠지는 피해운전자', loc='left', fontweight='bold', fontsize=10)
s = d.sort_values('ratio_all'); met = s.metro == 1
bx.barh(s.sido, s.ratio_all, color=[BLUE if m else RED for m in met], height=.72)
for y, v in enumerate(s.ratio_all): bx.text(v + .04, y, f'{v:.1f}배', va='center', fontsize=7.8)
bx.axvline(1, color=INK, lw=.9); bx.set_xlim(0, 3.2); bx.set_ylim(-0.7, 17.6); bx.tick_params(labelsize=8)
bx.set_xlabel('119 자전거 이송 ÷ 경찰 전체 부상(가해+피해 단순 합)', fontsize=8)
bx.set_title('(나) 경찰 통계 전체와 119의 차이', loc='left', fontweight='bold', fontsize=10)
M = R['metro_vs_other']
fig.legend(handles=[Patch(color=RED, label=f"도·세종 10곳  (가) 중앙값 {M['victim_share']['median_nonmetro']*100:.0f}%  (나) {M['ratio_all']['median_nonmetro']:.1f}배"),
                    Patch(color=BLUE, label=f"서울·광역시 7곳  (가) {M['victim_share']['median_metro']*100:.0f}%  (나) {M['ratio_all']['median_metro']:.1f}배")],
           loc='lower center', ncol=2, frameon=False, fontsize=8)
plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.savefig('figures/fig2_two_layers.png'); plt.close()

# 그림 4: 시설
fig, ax = plt.subplots(figsize=(7.6, 3.0), dpi=220)
ax.stackplot(ts.year, ts.dedicated_km, ts.shared_km, ts.other_km, colors=[BLUE, RED, '#C9CED4'], labels=['전용도로', '겸용도로(보행자와 공유)', '전용차로·우선도로'])
ax.set_ylabel('자전거도로 연장(km)', fontsize=8.5); ax.yaxis.set_major_formatter(comma); ax.legend(loc='upper left', frameon=False, fontsize=8.5); ax.tick_params(labelsize=8)
F = R['facility']
ax.text(2025, ts.total_km.iloc[-1] + 600, f"28,453km\n겸용 {F['shared_pct_2025']:.0f}%", ha='right', fontweight='bold', fontsize=8.5)
ax.text(2011, ts.total_km.iloc[0] + 600, f"15,307km\n겸용 {F['shared_pct_2011']:.0f}%", ha='left', fontweight='bold', fontsize=8.5)
ax.set_ylim(0, 35000); ax.set_xlim(2011, 2025)
ax.set_title('2011→2025년 1.9배로 늘었지만 4분의 3은 보행자와 함께 쓰는 길', loc='left', fontweight='bold', fontsize=10)
plt.tight_layout(); plt.savefig('figures/fig4_lane_composition.png'); plt.close()

# 그림 5: 시군구 228곳
import numpy as np
S = pd.read_csv('outputs/sgg_table.csv'); RS = json.load(open('outputs/results_sgg.json', encoding='utf-8'))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 4.0), dpi=220, gridspec_kw={'width_ratios': [1, 1.25]})
n20 = S[S.sum_inj >= 20]; rng = np.random.default_rng(1)
for i, (k, c, lab) in enumerate([('구', BLUE, '자치구'), ('시', GREY, '시'), ('군', RED, '군')]):
    g = n20[n20.kind == k]; v = g.victim_injured / g.sum_inj * 100       # 원 자료로 계산(반올림 전)
    a1.scatter(i + rng.uniform(-.17, .17, len(v)), v, s=12, color=c, alpha=.75, lw=0)
    a1.hlines(v.median(), i - .3, i + .3, color=INK, lw=2)
    a1.text(i, 112, f'중앙값 {v.median():.0f}%\n({len(v)}곳)', ha='center', va='top', fontsize=8, color=INK, fontweight='bold')
a1.set_xticks([0, 1, 2]); a1.set_xticklabels(['자치구', '시', '군'], fontsize=8.5); a1.set_ylim(0, 114); a1.set_yticks([0, 20, 40, 60, 80, 100]); a1.tick_params(labelsize=8)
a1.set_ylabel('피해운전자 비중(%)', fontsize=8.5)
a1.set_title(f"(가) 부상 20명 이상 {RS['n_sum20']}곳", loc='left', fontweight='bold', fontsize=9.5)
t8 = RS['top_ratio_vic15'][:8][::-1]
y = np.arange(len(t8))
a2.barh(y + .2, [r['vic'] for r in t8], height=.38, color=BLUE, label='피해운전자 부상')
a2.barh(y - .2, [r['off'] for r in t8], height=.38, color=GREY, label='공표 기준(가해운전자 부상)')
a2.set_yticks(y); a2.set_yticklabels([f"{r['sido']} {r['sgg']}" for r in t8], fontsize=8.5); a2.tick_params(axis='x', labelsize=8)
for yi, r in zip(y, t8):
    a2.text(r['vic'] + 1, yi + .2, str(r['vic']), va='center', fontsize=7.8); a2.text(r['off'] + 1, yi - .2, str(r['off']), va='center', fontsize=7.8)
a2.legend(frameon=False, fontsize=7.8, loc='lower right'); a2.set_xlim(0, 75)
a2.set_title('(나) 공표 대비 피해운전자 부상이 많은 곳', loc='left', fontweight='bold', fontsize=9.5)
plt.tight_layout(); plt.savefig('figures/fig5_sgg.png'); plt.close()
print('figures ok')
