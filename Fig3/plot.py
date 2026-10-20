from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('Fig3',needs_map=False);data=args.data
lm=read(data/'Fig3/LMG.csv');gl=read(data/'Fig3/GLM.csv');fig,axes=plt.subplots(2,3,figsize=(7.2,5.6),layout='constrained')
short={'Influent characteristics':'Influent','Climatic conditions':'Climate','Design parameters':'Design','Geographic region':'Region','Wastewater type':'Wastewater','Substrate type':'Substrate','CWs type':'CW type'}
terms=['tmean_ann','prec_ann','influent_COD','influent_NH4N','depth_m']
for i,gas in enumerate(GASES):
    d=lm[lm.gas.eq(gas)].sort_values('share_explained_percent');a=axes[0,i];a.barh(d.predictor_group.map(short),d.share_explained_percent,color=COLORS[i]);a.set(xlabel='Share of explained variation (%)',title=gas+f'; R² = {d.OLS_full_model_R2.iloc[0]:.2f}')
    d=gl[gl.gas.eq(gas)&gl.term.isin(terms)];a=axes[1,i];a.axvline(0,color='#aaa',lw=.5);a.errorbar(d.beta,np.arange(len(d)),xerr=np.array([d.beta-d.ci_low,d.ci_high-d.beta]),fmt='o',color=COLORS[i],ms=3,lw=.8);a.set(yticks=np.arange(len(d)),yticklabels=d.term.replace({'tmean_ann':'Temperature','prec_ann':'Precipitation','influent_COD':'COD','influent_NH4N':'NH₄–N','depth_m':'Depth'}),xlabel='Standardized coefficient (95% CI)')
labels(axes);save(fig,'Fig3_analytical_replot')
