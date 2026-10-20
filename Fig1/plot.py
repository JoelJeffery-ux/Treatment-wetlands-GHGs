"""Fig. 1: aggregated CW distribution and measured flux distributions."""
from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
from matplotlib.patches import Rectangle
from external_inputs import monitoring_climate

args=cm.setup('Fig1',needs_map=True);data=args.data/'Fig1'
obs=read(data/'flux_observations.csv');sites=read(data/'flux_monitoring_sites.csv')
grid=read(data/'inventory_hex.csv').set_index('h3_cell')
types=['FWSCW','HFCW','VFCW','HCW','FCW']
type_colors=['#5279aa','#5f9e72','#be5b5e','#8971ac','#c2b36a']
fig=plt.figure(figsize=(7.2,6.6),layout='constrained')
gs=fig.add_gridspec(2,3,height_ratios=[1.05,1])
ax=fig.add_subplot(gs[0,:2]);land(ax)
poly=[p for cell,p in zip(cm.CELLS,cm.POLYS) if cell in grid.index]
ax.add_collection(PolyCollection(poly,facecolor='#c4cbd1',edgecolor='white',linewidth=.2))
for typ,col in zip(types,type_colors):
    s=sites[sites.cw_type.eq(typ)]
    sizes=7+3*np.clip(np.log10(s.area_m2.fillna(100).clip(lower=1)),0,6)
    ax.scatter(s.longitude_deg,s.latitude_deg,s=sizes,color=col,edgecolor='white',linewidth=.3,label=f'{typ} (n={len(s)})',zorder=3)
ax.set_title('4,958 inventoried CW systems; 134 with flux records',loc='left')
ax.legend(loc='lower left',bbox_to_anchor=(0,-.23),ncol=3,fontsize=5.2,frameon=False,handletextpad=.3,columnspacing=.8)
ax.text(0,-.3,'Grey H3 cells: 4,824 systems without flux records',transform=ax.transAxes,fontsize=5.5)
ax.text(-.05,1.05,'a',transform=ax.transAxes,fontweight='bold',fontsize=8)
ac=fig.add_subplot(gs[0,2]);density=read(data/'climate_density.csv')
for r in density.itertuples():
    ac.add_patch(Rectangle((r.temperature_left_C,r.precipitation_bottom_mm),
        r.temperature_right_C-r.temperature_left_C,r.precipitation_top_mm-r.precipitation_bottom_mm,
        color=plt.cm.Greys(.12+.62*np.log1p(r.n)/np.log1p(density.n.max())),lw=0))
climate=monitoring_climate(read(data/'climate_sampling_locations.csv'),args.external_cache)
for typ,col in zip(types,type_colors):
    d=climate[climate.cw_type.eq(typ)]
    ac.scatter(d.mean_annual_temperature_C,d.annual_precipitation_mm,s=9,color=col,edgecolor='white',linewidth=.2)
ac.set(xlim=(-15,33),ylim=(0,4500),xlabel='Mean annual temperature (°C)',
       ylabel='Annual precipitation (mm)',title='Monitoring climate (n=84)')
rng=np.random.default_rng(10)
for i,gas in enumerate(GASES):
    a=fig.add_subplot(gs[1,i]);d=obs[obs.gas.eq(gas)]
    vals=[d[d.cw_type.eq(t)].flux_mg_m2_d.to_numpy() for t in types]
    boxes=a.boxplot(vals,labels=types,showfliers=False,patch_artist=True,
                    medianprops={'color':'black','linewidth':.8},
                    boxprops={'linewidth':.6},whiskerprops={'linewidth':.6},capprops={'linewidth':.6})
    for k,(arr,col,patch) in enumerate(zip(vals,type_colors,boxes['boxes']),1):
        patch.set_facecolor(col);patch.set_alpha(.4)
        positive=arr[arr>0]
        a.scatter(k+rng.uniform(-.23,.23,len(positive)),positive,s=3,color=col,alpha=.5,edgecolors='none')
        a.text((k-.5)/5,.98,f'n={len(arr)}',transform=a.transAxes,ha='center',va='top',fontsize=5.2)
    a.set_yscale('log');a.tick_params(axis='x',rotation=35)
    a.set_ylabel(gas+' flux (mg m⁻² d⁻¹)')
    a.margins(y=.15);a.text(-.15,1.03,'bcd'[i],transform=a.transAxes,fontweight='bold',fontsize=8)
save(fig)
