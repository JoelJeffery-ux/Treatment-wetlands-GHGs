from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('ED3',needs_map=False);data=args.data
centered=read(data/'Extended_Data/ED3/centered_GHG_records.csv');q=read(data/'Extended_Data/ED3/Q10_summary.csv');fig,axs=plt.subplots(1,3,figsize=(7.2,2.5),layout='constrained')
for i,gas in enumerate(GASES):
    d=centered[centered.gas.eq(gas)];r=q[q.gas.eq(gas)].iloc[0];a=axs[i];a.scatter(d.temperature_within_c,d.ln_flux_within,s=5,color=COLORS[i],alpha=.35);x=np.linspace(d.temperature_within_c.min(),d.temperature_within_c.max(),80);a.plot(x,r.beta_ln_per_c*x,c=COLORS[i]);a.set(xlabel='Within-case temperature (°C)',ylabel='Within-case ln(flux)',title=f'{gas}: Q₁₀ = {r.estimate:.2f} ({r.ci_low:.2f}–{r.ci_high:.2f})')
labels(axs);save(fig,'ED3_Q10')
