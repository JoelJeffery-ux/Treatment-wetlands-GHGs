from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('S02',needs_map=False);data=args.data
comp=read(data/'Supplementary/S02/comparison_summary.csv');fig,axs=plt.subplots(1,4,figsize=(7.2,3.6),layout='constrained')
for a,gas in zip(axs,['CH4','N2O','CO2','CO2e']):
    d=comp[comp.gas.eq(gas)&(~comp.ecosystem.eq('Constructed wetlands')|comp.estimator.eq('positive_measured_median')|comp.estimator.str.contains('composite'))].copy()
    # ML estimates are area-weighted means.
    if d.empty: a.set_visible(False);continue
    d=d.drop_duplicates('ecosystem')
    for k,r in enumerate(d.itertuples()):
        is_cw=r.ecosystem=='Constructed wetlands'
        if np.isfinite(r.lower_endpoint) and r.lower_endpoint>0:
            if is_cw:
                a.fill_betweenx([k-.22,k+.22],r.lower_endpoint,r.upper_endpoint,color='#ddd',zorder=1)
            else:
                a.plot([r.lower_endpoint,r.upper_endpoint],[k,k],c='#777',lw=.7)
        a.scatter([r.centre],[k],s=48 if is_cw else 10,marker='*' if is_cw else 'o',color='#695176',zorder=3)
        if is_cw:
            prediction=comp[comp.gas.eq(gas)&comp.ecosystem.eq('Constructed wetlands')&comp.estimator.eq('area_weighted_ML')]
            a.scatter(prediction.centre,[k+.12]*len(prediction),s=48,marker='*',facecolors='white',edgecolors='#695176',linewidths=.7,zorder=4)
            a.text(.97,.01,f'Measured: {r.centre:.1f}',transform=a.transAxes,ha='right',va='bottom',fontsize=5.2)
    a.set(yticks=np.arange(len(d)),yticklabels=(d.ecosystem if a is axs[0] else ['']*len(d)),xlabel=str(d.unit.iloc[0]),title=gas,xscale='log')
fig.suptitle('Filled stars: measured CW medians; open stars: area-weighted ML means\n'
             'CW CO₂-eq: unpaired component index; other systems: geometric mean and geometric SD',
             fontsize=6)
labels(axs);save(fig,'S02_ecosystem_comparison')
