"""Fig. 2: predicted fluxes, latitude distributions and continental totals."""
from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *

args=cm.setup('Fig2',needs_map=True);data=args.data/'Fig2'
hexflux=read(data/'hex_flux.csv').set_index('h3_cell')
lat=read(data/'latitude.csv');total=read(data/'continent_totals.csv')
short={'North America':'N. America','South America':'S. America'}
fig,axes=plt.subplots(3,3,figsize=(7.2,8),layout='constrained',gridspec_kw={'width_ratios':[2.1,.65,1.2]})
for i,gas in enumerate(GASES):
    div=1000 if gas=='CO2' else 1
    unit=('g' if div==1000 else 'mg')+' '+gas+' m⁻² d⁻¹'
    mapplot(axes[i,0],hexflux[gas+'_flux_mg_m2_d']/div,gas,unit)
    axes[i,0].text(-.07,1.05,'abc'[i],transform=axes[i,0].transAxes,fontweight='bold',fontsize=8)
    d=lat[lat.gas.eq(gas)]
    axes[i,1].plot(d.median_mg_m2_d/div,d.latitude_band_centre_deg,c=COLORS[i])
    axes[i,1].fill_betweenx(d.latitude_band_centre_deg,d.q25_mg_m2_d/div,d.q75_mg_m2_d/div,color=COLORS[i],alpha=.2)
    axes[i,1].set(xlabel=unit,ylabel='Latitude (°)',title='Median and IQR')
    d=total[total.gas.eq(gas)&total.region.ne('Global')].copy()
    a=axes[i,2];y=np.arange(len(d))
    a.barh(y-.18,d.total_t_yr/(1e6 if gas=='CO2' else 1000),height=.33,color=COLORS[i])
    a.set(yticks=y,yticklabels=d.region.replace(short),xlabel='Annual emissions\n'+('Tg' if gas=='CO2' else 'Gg')+' yr⁻¹')
    b=a.twiny();b.barh(y+.18,d.area_weighted_mean_mg_m2_d/div,height=.33,color=COLORS[i],alpha=.3)
    b.set_xlabel('Area-weighted mean\n'+unit,labelpad=3,fontsize=5.8)
    b.tick_params(labelsize=5);a.tick_params(axis='y',labelsize=5.4);a.invert_yaxis()
save(fig)
