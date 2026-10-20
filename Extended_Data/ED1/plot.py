"""Extended Data 1: case-level distributions, reconstructed from box statistics."""
from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('ED1');data=args.data/'Extended_Data/ED1'
stats=read(data/'box_statistics.csv');vd=read(data/'variables.csv').set_index('variable')
variables=list(vd.index);fig,axs=plt.subplots(int(np.ceil(len(variables)/4)),4,figsize=(7.2,8.8),layout='constrained')
for a,var in zip(axs.flat,variables):
    dd=stats[stats.variable.eq(var)].set_index('gas')
    bs=[]
    for gas in GASES:
        r=dd.loc[gas]
        bs.append(dict(label=gas,med=r['median'],q1=r.q25,q3=r.q75,whislo=r.whislo,whishi=r.whishi,fliers=[]))
    boxes=a.bxp(bs,showfliers=False,patch_artist=True)
    for b,c in zip(boxes['boxes'],COLORS):b.set_facecolor(c);b.set_alpha(.6)
    a.set_title(str(vd.loc[var,'label']),fontsize=6.2)
    if vd.loc[var,'display_scale']=='log10':a.set_yscale('log')
    a.set_ylabel(str(vd.loc[var,'unit']),fontsize=5.5)
for a in list(axs.flat)[len(variables):]:a.set_visible(False)
save(fig)
