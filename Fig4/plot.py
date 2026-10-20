from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('Fig4',needs_map=True);data=args.data
hexflux=read(data/'Fig2/hex_flux.csv').set_index('h3_cell')
annual=read(data/'Fig4/annual_members.csv')
lat=read(data/'Fig4/bd_Smooth_curve.csv')
hc=read(data/'Fig4/hex_changes_members.csv')
increase=read(data/'Fig4/ac_Global_change.csv')
names=dict(zip(SSPS,['SSP1-2.6','SSP2-4.5','SSP5-8.5']))
fig=plt.figure(figsize=(7.2,8.4),layout='constrained')
gs=fig.add_gridspec(4,4,height_ratios=[1,1,1,1])
def panel(ax,label):
    ax.text(-.07,1.10,label,transform=ax.transAxes,fontweight='bold',fontsize=8)
for row,gas in enumerate(['CH4','CO2']):
    div=1000 if gas=='CO2' else 1
    unit=('g' if div==1000 else 'mg')+' '+gas+' m⁻² d⁻¹'
    a=fig.add_subplot(gs[row,0])
    mapplot(a,hexflux[gas+'_flux_mg_m2_d']/div,gas+' F₀',unit);panel(a,'ac'[row])
    for j,ssp in enumerate(SSPS):
        a=fig.add_subplot(gs[row,j+1])
        d=hc[hc.gas.eq(gas)&hc.scenario.eq(ssp)].groupby('h3_cell').change_mg_m2_d.median()/div
        pct=increase[increase.gas.eq(gas)&increase.scenario.eq(names[ssp])].global_total_change_percent.iloc[0]
        mapplot(a,d,names[ssp]+' ΔF\n'+f'Global increase: {pct:.2f}%',unit,False)
    a=fig.add_subplot(gs[2,row*2:row*2+2])
    b=fig.add_subplot(gs[3,row*2:row*2+2])
    panel(a,'bd'[row]);panel(b,'ef'[row])
    for ssp,c in zip(SSPS,SC):
        d=lat[lat.gas.eq(gas)&lat.scenario.eq(names[ssp])].sort_values('latitude_deg')
        a.plot(d.latitude_deg,d.display_median,color=c,label=names[ssp])
        a.fill_between(d.latitude_deg,d.display_GCM_min,d.display_GCM_max,color=c,alpha=.15)
        d=annual[annual.gas.eq(gas)&annual.scenario.eq(ssp)].groupby('year').total
        b.plot(d.median().index,d.median(),color=c,label=names[ssp])
        b.fill_between(d.median().index,d.min(),d.max(),color=c,alpha=.15)
    a.set(xlabel='Latitude (°)',ylabel='ΔF ('+unit+')')
    a.legend(frameon=False,fontsize=5)
    b.axvspan(2015,2025,color='#ddd',zorder=0)
    b.set(xlabel='Year',ylabel=gas+(' (Tg yr⁻¹)' if gas=='CO2' else ' (Gg yr⁻¹)'))
    b.legend(frameon=False,fontsize=5)
save(fig)
