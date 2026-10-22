"""그림 3(지도): 시도 17곳의 인구 10만 명당 자전거 부상 순위를 세 집계(공표·경찰 전체·119)로 칠한다.
먼저 python analysis.py 실행. 필요: geopandas.
경계: data/boundary_sido_2025.geojson · boundary_sgg_2025.geojson — vuski/admdongkor ver20250401 행정동 경계(통계청 SGIS 기반)를 시도·시군구로 합친 것."""
import glob
import pandas as pd, geopandas as gpd, matplotlib
import matplotlib.patheffects as pe
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, Normalize
for f in glob.glob('/usr/share/fonts/**/*CJK*.ttc', recursive=True) + glob.glob('/usr/share/fonts/**/Nanum*.ttf', recursive=True):
    fm.fontManager.addfont(f)
names = {f.name for f in fm.fontManager.ttflist}
plt.rcParams['font.family'] = next((n for n in ['Noto Sans CJK KR', 'NanumGothic', 'Malgun Gothic', 'AppleGothic'] if n in names), 'sans-serif')
INK = '#1F2933'
geo = gpd.read_file('data/boundary_sido_2025.geojson')
r = pd.read_csv('outputs/region_table.csv')
m = geo.merge(r, on='sido', how='left'); assert m.population.notna().all() and len(m) == 17
cmap = LinearSegmentedColormap.from_list('r', ['#8E2A14', '#D9482B', '#F4B49A', '#FBEFE8'])   # 1위(많음)=진함
norm = Normalize(1, 17)
CALL = {'서울': (125.75, 38.05), '인천': (125.35, 37.35), '세종': (126.0, 36.75), '대전': (126.15, 36.2),
        '광주': (125.6, 35.25), '대구': (129.85, 36.05), '울산': (129.95, 35.6), '부산': (129.55, 34.85)}
HL = ('전북', '경북', '서울')
fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.55), dpi=230)
for ax, col, title in [(axes[0], 'rank_rate_pub', '① 공표 기준(가해자 부상)'), (axes[1], 'rank_rate_all', '② 경찰 전체(가해+피해)'), (axes[2], 'rank_rate_119', '③ 119 구급 이송')]:
    m.plot(column=col, cmap=cmap, norm=norm, ax=ax, edgecolor='white', linewidth=0.5)
    for _, row in m.iterrows():
        pt = row.geometry.representative_point(); rk = int(row[col]); hl = row.sido in HL
        fw = 'bold'; fs = 7.6 if hl else 6.4; colr = '#0B3D91' if hl else INK
        if row.sido in CALL:
            lx, ly = CALL[row.sido]
            ax.plot([pt.x, lx], [pt.y, ly], color='#9AA3AD', lw=0.4, zorder=3)
            ax.text(lx, ly, f"{row.sido} {rk}", ha='center', va='center', fontsize=fs, fontweight=fw, color=colr,
                    bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85), zorder=4)
        else:
            ax.text(pt.x, pt.y, f"{row.sido}\n{rk}", ha='center', va='center', fontsize=fs, fontweight=fw,
                    color='white' if rk <= 6 else colr, linespacing=0.9, zorder=4, path_effects=[pe.withStroke(linewidth=1.6, foreground=('#5A1A0C' if rk <= 6 else 'white'))])
    ax.set_xlim(124.9, 130.4); ax.set_ylim(33.0, 38.7)
    ax.set_title(title, fontsize=8.8, fontweight='bold', color=INK); ax.axis('off')
fig.suptitle('인구 10만 명당 자전거 부상 순위 (숫자=순위, 진할수록 부상이 많음)', fontsize=9.5, fontweight='bold', color=INK, y=0.995)
plt.tight_layout(rect=(0, 0, 1, 0.95), w_pad=0.2); plt.savefig('figures/fig3_rank_map.png'); plt.close()
print('map ok')
