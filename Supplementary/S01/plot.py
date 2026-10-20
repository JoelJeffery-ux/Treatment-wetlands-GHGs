from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('S01',needs_map=False);data=args.data
total=read(data/'Fig2/continent_totals.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.2),layout='constrained');regions=total[total.gas.eq('CH4')&total.region.ne('Global')].region.to_list();base=total[total.gas.eq('CH4')].set_index('region');area=base.reindex(regions).area_km2/base.loc['Global','area_km2']*100;x=np.arange(len(regions));axs[0].bar(x-.27,area,.18,label='Area',color='#a8a8a8')
for i,gas in enumerate(GASES):
    d=total[total.gas.eq(gas)].set_index('region');share=100*d.reindex(regions).total_t_yr/d.loc['Global','total_t_yr'];axs[0].bar(x-.09+i*.18,share,.18,label=gas,color=COLORS[i]);axs[1].plot(x,share/area,'o-',label=gas,color=COLORS[i],ms=3)
for a in axs:a.set_xticks(x,regions,rotation=45,ha='right');a.legend(frameon=False,fontsize=5)
axs[0].set_ylabel('Share of inventoried total (%)');axs[1].set_ylabel('Emission share / area share');axs[1].axhline(1,lw=.5,c='#aaa');labels(axs);save(fig,'S01_continent_area_intensity')
