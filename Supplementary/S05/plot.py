from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('S05',needs_map=False);data=args.data
oof=read(data/'Supplementary/S05/held_out_predictions.csv')
fig,axs=plt.subplots(1,3,figsize=(7.2,3.1),layout='constrained')
rows=[]
for a,gas in zip(axs,GASES):
    for model,d in oof[oof.gas.eq(gas)].groupby('model'):
        m=d.groupby('case_id')[['y_log10','oof_log10']].mean();r2=1-((m.y_log10-m.oof_log10)**2).sum()/((m.y_log10-m.y_log10.mean())**2).sum();rows.append(dict(gas=gas,model=model,R2_cases=r2))
    ss=pd.DataFrame(rows).query('gas==@gas');a.barh(ss.model,ss.R2_cases,color=COLORS[GASES.index(gas)]);a.axvline(0,lw=.5,c='#999');a.set(xlabel='Case-mean held-out R²',title=gas+' candidate models')
labels(axs);save(fig,'S05_candidate_model_comparison');pd.DataFrame(rows).to_csv(cm.OUT/'candidate_metrics_recomputed.csv',index=False)
