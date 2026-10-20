"""Load management source tables and provide plotting functions."""
from pathlib import Path
import os, json, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.colors import LogNorm, LinearSegmentedColormap
import fitz


import common as cm
from external_inputs import load_land
DATA=Path(os.environ['CW_FIGURE_DATA'])
O=cm.OUT
(O/'validation').mkdir(exist_ok=True)
POL=['C','N','D','CN','OPT'];ALLPOL=['CU']+POL
CONT=['Asia','North America','Europe','Oceania','Africa','South America']
S=pd.read_csv(DATA/'Supplementary/S03/all_global_totals.csv')
S['scope']='reconstructed';S['changed_records']=S.selected_records
S=S.set_index(['scope','policy'])
G=pd.read_csv(DATA/'Supplementary/S03/continent_totals.csv')
allhex=pd.read_csv(DATA/'Supplementary/S03/all_map_cells.csv')
H={k:z.set_index('h3_cell') for k,z in allhex.groupby('policy')}
LAND=load_land(Path(os.environ['CW_EXTERNAL_CACHE']))
vertices=pd.read_csv(DATA/'Map_geometry/hex_vertices.csv')
features=[]
for cell,z in vertices.groupby('h3_cell'):
    if cell not in H['OPT'].index:continue
    coords=z.sort_values('vertex_order')[['longitude_deg','latitude_deg']].to_numpy().tolist()
    if coords[0]!=coords[-1]:coords.append(coords[0])
    features.append({'type':'Feature','properties':{'h3_cell':cell},
                     'geometry':{'type':'Polygon','coordinates':[coords]}})
HEXGEO={'type':'FeatureCollection','features':features}
INK='#233744';NAVY='#244E67';MUTED='#637885';RULE='#D5DFE3'
GAS1='#85579A';GAS2='#C38936';NEG='#BA704B'
MAPCOL=['#A4CECA','#6BAEB4','#3D899E','#28657F','#163E58']
MAPSIZE=np.array([5,8,12,19,29.])
ZERO='#CDD1D6';LANDCOLOR='#F2F3F3';COAST='#B4BFC7'
STRATEGY={'C':'#BA8D4B','N':'#728CB1','D':'#3E968A','CN':'#9380A9','OPT':NAVY}
SEQ=LinearSegmentedColormap.from_list('cw_teal_navy',['#EDF5F3','#B7D8D0','#73ADB1','#397C95','#193F5A'])
HEXCMAP=LinearSegmentedColormap.from_list('hex_teal_navy',['#C9E4DD','#89C1B6','#479B9D','#286981','#123950'])
HEXNORM=LogNorm(vmin=1e-4,vmax=1e5)
BASENORM=LogNorm(vmin=.1,vmax=100)
plt.rcParams.update({'font.family':'Arial','font.size':6,'axes.labelsize':6,'xtick.labelsize':5.6,'ytick.labelsize':5.6,
 'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':MUTED,
 'axes.linewidth':.5,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
 'xtick.major.size':2,'ytick.major.size':2,'xtick.major.width':.5,'ytick.major.width':.5,
 'pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'custom','mathtext.rm':'Arial',
 'mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold','savefig.facecolor':'white'})


def dump(obj,path):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def figure(h):
    f=plt.figure(figsize=(183/25.4,h/25.4),dpi=160);f._h=h;return f
def axis(f,x,y,w,h):return f.add_axes([x/183,1-(y+h)/f._h,w/183,h/f._h])
def txt(f,x,y,s,fs=6,**kw):return f.text(x/183,1-y/f._h,s,fontsize=fs,va=kw.pop('va','top'),**kw)
def line(f,x1,y1,x2,y2,color=RULE,lw=.5):
    f.add_artist(Line2D([x1/183,x2/183],[1-y1/f._h,1-y2/f._h],transform=f.transFigure,color=color,lw=lw))
def rect(f,x,y,w,h,fc,ec='none',lw=.5):
    f.add_artist(Rectangle((x/183,1-(y+h)/f._h),w/183,h/f._h,transform=f.transFigure,fc=fc,ec=ec,lw=lw))
def panel(f,x,y,l,title):txt(f,x,y,l,8,fontweight='bold');txt(f,x+5,y+.2,title,6.7,fontweight='bold')
def point(f,x,y,c,s):
    f.add_artist(Line2D([x/183],[1-y/f._h],transform=f.transFigure,marker='o',markersize=np.sqrt(s),
                  markeredgecolor='white',markeredgewidth=.15,markerfacecolor=c,ls=''))


def save(f,name):
    f.canvas.draw()
    ren=f.canvas.get_renderer();outside=[]
    for t in f.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():continue
        bb=t.get_window_extent(ren)
        if bb.width<=0 or bb.height<=0:continue
        if bb.x0<-.5 or bb.y0<-.5 or bb.x1>f.bbox.width+.5 or bb.y1>f.bbox.height+.5:outside.append(t.get_text())
    dump({'text_outside_canvas':outside},O/'validation/layout.json')
    cm.save(f)
