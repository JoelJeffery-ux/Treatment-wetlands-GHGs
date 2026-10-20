"""Extended Data 2: annual emissions summed within published map cells."""
from pathlib import Path
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
args=cm.setup('ED2',needs_map=True)
d=read(args.data/'Extended_Data/ED2/hex_annual_totals.csv').set_index('h3_cell')
fig,axs=plt.subplots(2,2,figsize=(7.2,5.6),layout='constrained')
for i,gas in enumerate(GASES):mapplot(axs.flat[i],d[gas+'_annual_t'],gas+' annual emissions','t yr⁻¹')
masses=np.array([d[g+'_annual_t'].sum()*w for g,w in zip(GASES,[27.2,273,1])])
axs[1,1].bar(GASES,masses/1e6,color=COLORS);axs[1,1].set_ylabel('Tg CO₂-eq yr⁻¹')
axs[1,1].set_title(f'Total: {masses.sum()/1e6:.2f} Tg CO₂-eq yr⁻¹',loc='left')
labels(axs);save(fig)
