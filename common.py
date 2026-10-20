"""Shared plotting functions for CW greenhouse-gas figures."""
from pathlib import Path
import json, string
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm,Normalize
from matplotlib.patches import Polygon
GASES=['CH4','N2O','CO2'];COLORS=['#8564a6','#cfaa3d','#5b9b7b']
SSPS=['ssp126','ssp245','ssp585'];SC=['#418a9a','#d39c42','#bd5359']
def read(p):return pd.read_csv(p,low_memory=False)
def save(fig,name=None):
    name=FIGURE_ID
    fig.savefig(OUT/(name+'.pdf'));fig.savefig(OUT/(name+'.svg'));fig.savefig(OUT/(name+'.png'),dpi=300);plt.close(fig)
def labels(axes):
    for a,l in zip(np.ravel(axes),string.ascii_lowercase):a.text(-.07,1.05,l,transform=a.transAxes,fontweight='bold',fontsize=8,va='bottom')
def land(ax):
    for item in LAND['features']:
        geo=item['geometry'];polys=geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]
        for poly in polys:ax.add_patch(Polygon(poly[0],facecolor='#efefef',edgecolor='#c2c6c9',lw=.2,zorder=0))
    ax.set(xlim=(-180,180),ylim=(-60,85));ax.set_xticks([-120,0,120]);ax.set_yticks([-30,30,70]);ax.set_aspect('equal')
    ax.tick_params(length=2);ax.spines[['top','right','bottom','left']].set_visible(False)
def mapplot(ax,values,title,unit,log=True):
    land(ax);v=pd.Series(values).reindex(CELLS).to_numpy(float);finite=v[np.isfinite(v)]
    norm=LogNorm(max(np.min(finite[finite>0]),1e-4),np.max(finite)) if log else Normalize(min(0,np.min(finite)),np.max(finite))
    pc=PolyCollection(POLYS,array=v,cmap='viridis' if log else 'YlOrRd',norm=norm,edgecolors='none',zorder=2)
    ax.add_collection(pc);ax.set_title(title,loc='left',fontsize=7)
    cb=ax.figure.colorbar(pc,ax=ax,orientation='horizontal',pad=.08,fraction=.07,shrink=.82);cb.set_label(unit,fontsize=6);cb.ax.tick_params(labelsize=5,length=2)

def setup(figure_id, needs_map=False):
    global OUT,LAND,CELLS,POLYS,FIGURE_ID
    import argparse,os
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,default=Path(__file__).resolve().parent.parent/'figshare_data')
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent.parent/'reproduced_figures')
    parser.add_argument('--external-cache',type=Path,default=Path(__file__).resolve().parent.parent/'external_cache')
    args=parser.parse_args();FIGURE_ID=figure_id
    OUT=args.out/figure_id;OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':6.5,'axes.labelsize':6.5,'axes.titlesize':7,
      'xtick.labelsize':5.5,'ytick.labelsize':5.5,'axes.linewidth':.5,
      'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
    if needs_map:
        from external_inputs import load_land
        LAND=load_land(args.external_cache)
        v=read(args.data/'Map_geometry/hex_vertices.csv');CELLS=[];POLYS=[]
        for cell,d in v.groupby('h3_cell',sort=True):
            CELLS.append(cell);POLYS.append(d.sort_values('vertex_order')[['plotting_longitude_deg','latitude_deg']].to_numpy())
    return args
