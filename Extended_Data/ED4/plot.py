from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('ED4',needs_map=False);data=args.data
lat=read(data/'Fig4/latitude_members.csv')
fig,axs=plt.subplots(2,2,figsize=(7.2,5),layout='constrained')
for row,gas in enumerate(['CH4','CO2']):
    for col,value in enumerate(['change_mg_m2_d','total_change_t_yr']):
        a=axs[row,col]
        for ssp,c in zip(SSPS,SC):
            d=lat[lat.gas.eq(gas)&lat.scenario.eq(ssp)].groupby('latitude_midpoint_deg')[value];a.plot(d.median().index,d.median(),color=c,label=ssp);a.fill_between(d.median().index,d.min(),d.max(),color=c,alpha=.15)
        a.set(xlabel='Latitude (°)',ylabel=gas+(' flux increase (mg m⁻² d⁻¹)' if col==0 else ' total increase (t yr⁻¹)'));a.legend(frameon=False,fontsize=5)
labels(axs);save(fig,'ED4_latitude_flux_and_totals')
