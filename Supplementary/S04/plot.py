"""Draw the literature-screening diagram from the reported counts."""
from pathlib import Path
import sys,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
from common import *
from matplotlib.patches import FancyBboxPatch
args=cm.setup('S04')
n=json.loads((args.data/'Supplementary/S04/screening_counts.json').read_text(encoding='utf8'))
fig=plt.figure(figsize=(7.2,8.6));ax=fig.add_axes([.02,.02,.96,.96]);ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
def box(x,y,w,h,text,shade=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3',lw=.6,fc='#f0f2f2' if shade else 'white'))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=7,linespacing=1.35)
def arrow(x,y,X,Y):ax.annotate('',xy=(X,Y),xytext=(x,y),arrowprops={'arrowstyle':'-|>','lw':.6,'color':'#555'})
ax.text(1,98,'a  Global constructed wetland inventory',fontsize=9,fontweight='bold')
box(2,82,42,12,f"International database records\nn = {n['international']:,}\nPubMed 2,392; Scopus 1,933; Web of Science 2,986")
box(56,82,42,12,f"Chinese database records (CNKI)\nn = {n['CNKI']:,}")
box(2,67,42,8,f"Retained after deduplication\nn = {n['international_retained']:,}")
box(56,67,42,8,f"Retained after screening\nn = {n['CNKI_retained']:,}")
arrow(23,82,23,75);arrow(77,82,77,75)
ax.text(24,78,'1,453 duplicates removed',fontsize=5.5);ax.text(78,78,'10,545 excluded',fontsize=5.5,ha='center')
box(27,54,46,8,f"Candidate CW entries\nn = {n['candidate_entries']:,}",True)
ax.plot([23,23,77,77],[67,64,64,67],lw=.6,c='#555');arrow(50,64,50,62)
box(27,38,46,8,f"Global CW inventory\n{n['inventory_entries']:,} entries",True)
arrow(50,54,50,46)
ax.text(53,50,'3,287 excluded after deduplication\nand coordinate checks',fontsize=6,va='center')
ax.text(1,34,'b  Constructed wetland GHG flux dataset',fontsize=9,fontweight='bold')
box(2,22,42,8,f"English-language flux records\nn = {n['English_flux_records']:,}")
box(56,22,42,8,f"Chinese-language flux records\nn = {n['Chinese_flux_records']:,}")
box(27,12,46,7,f"Pooled flux records\nn = {n['pooled_flux_records']:,}",True)
ax.plot([23,23,77,77],[22,20.5,20.5,22],lw=.6,c='#555');arrow(50,20.5,50,19)
box(27,0,46,7,f"Type-resolved figure dataset\n{n['typed_flux_records']:,} flux records",True)
arrow(50,12,50,7)
ax.text(53,9.5,'794 exclusions from the typed figure subset',fontsize=5.8,va='center')
save(fig)
