"""Management maps for supplementary figures S03 and S08."""
from pathlib import Path
import json, hashlib, zipfile, platform
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection,PatchCollection
from matplotlib.patches import Polygon,Rectangle
from matplotlib.colors import LinearSegmentedColormap,LogNorm,ListedColormap,Normalize
from matplotlib.lines import Line2D
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
import fitz
import _management_core as b

O=b.O
INK='#202E38';MUTED='#657681';NAVY='#355E76';ZERO='#CAD0D6'
LAND='#F3F4F2';COAST='#ACB5B6';OCEAN='#FFFFFF';RULE='#D9E0E5'
CMAP=LinearSegmentedColormap.from_list('sand_ochre_burgundy',['#F6E6B2','#D9AE61','#B76D3C','#7E3F3B','#33283C'])
NORM=LogNorm(1e-4,1e5);BASE_NORM=LogNorm(.1,100)
MAP_COLORS=['#E4EDCB','#B9D3AD','#7EB7A6','#468F9C','#2B6380','#233955']
MAP_BREAKS=np.array([1.,10.,100.,1000.,10000.])
MAP_LABELS=['>0–<1','1–<10','10–<100','100–<1,000','1,000–<10,000','≥10,000']
MAP_AUDIT=[]
def mapcolor(value):
    return MAP_COLORS[int(np.searchsorted(MAP_BREAKS,value,side='right'))] if value>0 else ZERO
PROJECTIONS={'Robinson':'ESRI:54030','Equal Earth':'EPSG:8857',
 'Winkel Tripel':'+proj=wintri +datum=WGS84','Plate Carree':'+proj=eqc +datum=WGS84'}
DISPLAY='Equal Earth';EXTENT=(-180,-55,180,75)
POL=b.POL;CONT=b.CONT
SHORT=['Asia','N. America','Europe','Oceania','Africa','S. America']
ABBR=['AS','NA','EU','OC','AF','SA']
POL_TITLE={'C':'C  |  COD control','N':'N  |  Ammonium control','D':'D  |  Depth–HRT adjustment',
 'CN':'CN  |  Joint inlet control','OPT':'OPT  |  Combined management','CU':'CU  |  Current management'}
GAS1='#85579A';GAS2='#C38936'
plt.rcParams.update({'font.size':6,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK})
txt=b.txt;axis=b.axis;line=b.line;rect=b.rect;panel=b.panel
def parts(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for q in getattr(g,'geoms',[]) for p in parts(q)]

CACHE={}
def geometry(proj=DISPLAY,extent=EXTENT):
    key=(proj,extent)
    if key in CACHE:return CACHE[key]
    crs=PROJECTIONS.get(proj,proj)
    tr=Transformer.from_crs('EPSG:4326',crs,always_xy=True)
    cut=box(*extent);land=[];cells=[];owners=[]
    for ft in b.LAND['features']:
        for p in parts(shape(ft['geometry']).intersection(cut)):
            land.append(np.asarray(transform(tr.transform,p).exterior.coords))
    for ft in b.HEXGEO['features']:
        for p in parts(shape(ft['geometry']).intersection(cut)):
            cells.append(np.asarray(transform(tr.transform,p).exterior.coords));owners.append(ft['properties']['h3_cell'])
    x0,y0,x1,y1=extent
    ring=np.vstack([np.c_[np.linspace(x0,x1,361),np.full(361,y0)],
        np.c_[np.full(181,x1),np.linspace(y0,y1,181)],
        np.c_[np.linspace(x1,x0,361),np.full(361,y1)],
        np.c_[np.full(181,x0),np.linspace(y1,y0,181)]])
    fx,fy=tr.transform(ring[:,0],ring[:,1]);frame=np.c_[fx,fy]
    CACHE[key]=(tr,land,cells,owners,frame)
    return CACHE[key]

def world(f,x,y,w,h,k='OPT',proj=DISPLAY,extent=EXTENT,base=False,insets=False):
    ax=axis(f,x,y,w,h);tr,land,cells,owners,frame=geometry(proj,extent)
    ax.add_patch(Polygon(frame,closed=True,fc=OCEAN,ec=COAST,lw=.35,zorder=0))
    ax.add_collection(PolyCollection(land,facecolors=LAND,edgecolors=COAST,lw=.22,zorder=1))
    vals=b.H[k].loc[owners,'before_I' if base else 'saving_t'].to_numpy()
    ax.add_collection(PolyCollection(cells,facecolors=[CMAP(BASE_NORM(v)) if base and v>0 else mapcolor(v) for v in vals],
        edgecolors='white',linewidths=.17 if w<100 else .26,zorder=2,rasterized=False))
    ax.set(xlim=(frame[:,0].min(),frame[:,0].max()),ylim=(frame[:,1].min(),frame[:,1].max()),aspect='equal');ax.axis('off')
    if insets:
        for title,e,pr in INSETS:
            xa,ya,xb,yb=e
            ring=np.vstack([np.c_[np.linspace(xa,xb,81),np.full(81,ya)],np.c_[np.full(81,xb),np.linspace(ya,yb,81)],
                np.c_[np.linspace(xb,xa,81),np.full(81,yb)],np.c_[np.full(81,xa),np.linspace(yb,ya,81)]])
            xx,yy=tr.transform(ring[:,0],ring[:,1]);ax.plot(xx,yy,color=NAVY,lw=.55,zorder=4,ls=(0,(2,1.5)))
    MAP_AUDIT.append({'figure_id':id(f),'policy':k,'extent':list(extent),'projection':proj,'axis':ax,'cells':cells,'owners':owners})
    return ax

def colorbar(f,x,y,w,base=False,title=True):
    if title:txt(f,x,y,('Area-weighted intensity (g CO$_2$-eq m$^{-2}$ d$^{-1}$)' if base else 'Avoided emissions (t CO$_2$-eq yr$^{-1}$ cell$^{-1}$)'),5.5)
    ca=axis(f,x+2,y+4.2,w,1.8)
    ticks=[.1,1,10,100] if base else [1e-4,.01,1,100,10000,100000]
    cb=f.colorbar(matplotlib.cm.ScalarMappable(norm=BASE_NORM if base else NORM,cmap=CMAP),cax=ca,
        orientation='horizontal',extend='neither' if base else 'min',ticks=ticks)
    cb.solids.set_rasterized(False);cb.solids.set_edgecolor('face');cb.outline.set_linewidth(.35)
    cb.ax.minorticks_off();cb.ax.tick_params(length=1.4,pad=1,labelsize=5.1)
    return cb

def save(f,name):b.save(f,name)

def map_legend(f,y):
    txt(f,4,y,'Avoided emissions (t CO$_2$-eq yr$^{-1}$ per H3 cell)',6)
    for i,(color,label) in enumerate(zip(MAP_COLORS,MAP_LABELS)):
        x=4+i*20.5
        rect(f,x,y+5,19,2.8,color)
        txt(f,x+9.5,y+8.6,label,5.7,ha='center')
    rect(f,133,y+5,4,2.8,ZERO)
    txt(f,140,y+5.1,'No selected reduction',5.9)

def audit_map_sizes(f,name):
    f.canvas.draw();out=[]
    for item in MAP_AUDIT:
        if item['figure_id']!=id(f):continue
        ax=item['axis']; widths=[];areas=[]
        for vertices in item['cells']:
            xy=ax.transData.transform(vertices)/f.dpi*25.4
            widths.append(float(np.ptp(xy[:,0])))
            areas.append(float(abs(np.dot(xy[:,0],np.roll(xy[:,1],1))-np.dot(xy[:,1],np.roll(xy[:,0],1)))/2))
        pos=ax.get_position()
        out.append({k:item[k] for k in ['policy','extent','projection']}|{
            'axis_width_mm':pos.width*183,'axis_height_mm':pos.height*f._h,
            'median_polygon_width_mm':float(np.median(widths)),
            'median_polygon_area_mm2':float(np.median(areas)), 'polygon_parts':len(widths),
            'unique_cells_displayed':len(set(item['owners']))})
    b.dump(out,O/'validation'/f'{name}_map_sizes.json')

def atlas():
    f=b.figure(221);r=b.S.loc[('reconstructed','OPT')]
    panel(f,3,3,'a','Where combined management (OPT) reduces emissions')
    txt(f,8,10,f'{r.saving_t/1000:.2f} kt CO$_2$-eq yr$^{{-1}}$ avoided  |  {r.reduction_pct:.2f}% of CU  |  {int(r.changed_records):,} selected records',7)
    ax=world(f,3,18,177,68,'OPT',insets=True)
    tr=geometry()[0]
    for label,(_,ex,_) in zip('bcd',INSETS):
        x,y=tr.transform(ex[0],ex[3])
        ax.annotate(label,(x,y),xytext=(-2,2),textcoords='offset points',ha='right',va='bottom',fontsize=7,fontweight='bold',color=NAVY,
                    bbox=dict(fc='white',ec='none',pad=.5))
    map_legend(f,87)
    for i,(title,ex,pr) in enumerate(INSETS):
        x=3+i*60.1
        panel(f,x,105,'bcd'[i],title)
        world(f,x,111,56.5,34,'OPT',proj=pr,extent=ex)
    txt(f,4,146.2,'Same H3 cells and colour classes at both scales; regional windows retain full-cell values.',5.8,color=MUTED)
    line(f,3,151,180,151,lw=.5)
    panel(f,3,154,'e','Global mitigation by strategy')
    panel(f,98,154,'f','Continental savings')
    txt(f,8,161,'CH$_4$',6,color=GAS1);rect(f,4,161.5,2.5,1.8,GAS1)
    txt(f,25,161,'N$_2$O',6,color=GAS2);rect(f,21,161.5,2.5,1.8,GAS2)
    txt(f,86,161,'kt  |  % of CU',5.8,ha='right')
    ax=axis(f,14,169,48,31)
    rows=b.S.loc['reconstructed'].loc[POL]
    ax.barh(range(5),rows.CH4_saving_CO2e_t/1000,color=GAS1,height=.58)
    ax.barh(range(5),rows.N2O_saving_CO2e_t/1000,left=rows.CH4_saving_CO2e_t/1000,color=GAS2,height=.58)
    ax.set(xlim=(0,80),ylim=(4.55,-.55));ax.set_yticks(range(5),POL)
    ax.tick_params(axis='y',length=0,pad=4,labelsize=6.4);ax.spines['left'].set_visible(False)
    ax.set_xticks([0,20,40,60,80]);ax.tick_params(axis='x',labelsize=5.8)
    ax.set_xlabel('Avoided emissions (kt CO$_2$-eq yr$^{-1}$)',fontsize=5.9,labelpad=3)
    for i,row in enumerate(rows.itertuples()):
        ax.text(1.08,i,f'{row.saving_t/1000:.2f} | {row.reduction_pct:.2f}%',transform=ax.get_yaxis_transform(),fontsize=6,va='center')
    for t in ax.get_yticklabels():
        if t.get_text()=='OPT':t.set_fontweight('bold')
    txt(f,103,161,'Values: kt CO$_2$-eq yr$^{-1}$; colour: % of regional CU',5.7)
    matrix=b.G.pivot(index='policy',columns='map_continent_six',values='reduction_pct').loc[POL,CONT].to_numpy()
    values=b.G.pivot(index='policy',columns='map_continent_six',values='saving_t').loc[POL,CONT].to_numpy()/1000
    cmap=LinearSegmentedColormap.from_list('relative_blue',['#F3F6F8','#9EBBCD','#315F7F'])
    ax=axis(f,106,169,73,31)
    ax.pcolormesh(np.arange(7)-.5,np.arange(6)-.5,matrix,cmap=cmap,norm=Normalize(0,8),rasterized=False)
    ax.set(xlim=(-.5,5.5),ylim=(4.5,-.5))
    ax.set_yticks(range(5),POL);ax.set_xticks(range(6),ABBR)
    ax.tick_params(length=0,pad=3,labelsize=6)
    for sp in ax.spines.values():sp.set_visible(False)
    for i in range(5):
        for j in range(6):
            text=f'{values[i,j]:.3f}' if values[i,j]>=.001 else '<0.001'
            ax.text(j,i,text,ha='center',va='center',fontsize=5.8,color='white' if matrix[i,j]>=5 else INK,
                    fontweight='bold' if i==4 else 'normal')
    ax.set_xticks(np.arange(-.5,6,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True)
    ax.grid(which='minor',color='white',lw=1);ax.tick_params(which='minor',length=0)
    ca=axis(f,121,207,49,1.8)
    cb=f.colorbar(matplotlib.cm.ScalarMappable(norm=Normalize(0,8),cmap=cmap),cax=ca,orientation='horizontal',ticks=[0,2,4,6,8])
    cb.solids.set_rasterized(False);cb.solids.set_edgecolor('face');cb.outline.set_linewidth(.3);cb.ax.tick_params(labelsize=5.6,length=1.5,pad=1)
    txt(f,106,207,'% of CU',5.7)
    txt(f,4,216,'4,939 inventory records · q50 inputs · ≤5% relative removal loss · direct CH$_4$ + N$_2$O',5.8)
    audit_map_sizes(f,'Fig1_policy_management');save(f,'Fig1_policy_management')

INSETS=[('North America',(-125,22,-65,55),'+proj=laea +lat_0=38 +lon_0=-95 +datum=WGS84'),
 ('Europe',(-15,32,40,65),'+proj=laea +lat_0=49 +lon_0=12 +datum=WGS84'),
 ('East Asia',(95,10,145,50),'+proj=laea +lat_0=30 +lon_0=120 +datum=WGS84')]

def derived():
    acts=pd.read_csv(b.DATA/'Supplementary/S08/action_cohorts.csv')
    rank=pd.read_csv(b.DATA/'Supplementary/S08/ranked_cells.csv')
    return acts,rank

def detail():
    acts,rank=derived();f=b.figure(220)
    for i,k in enumerate(POL):
        x=3+(i%2)*91;y=3+(i//2)*54
        panel(f,x,y,'abcde'[i],POL_TITLE[k])
        world(f,x,y+6,85,35,k)
        r=b.S.loc[('reconstructed',k)]
        txt(f,x+4,y+44,f'{r.saving_t/1000:.2f} kt yr$^{{-1}}$  |  {r.reduction_pct:.2f}% of CU  |  n = {int(r.changed_records):,}',5.8)
    panel(f,94,111,'f','Selected action sets within OPT')
    aa=acts.set_index('action_set').reindex(['C','N','D','C+N','C+D','N+D','C+N+D'])
    ax=axis(f,115,120,48,33)
    ax.barh(range(7),aa.saving_t/1000,color=NAVY,height=.58)
    ax.set(xlim=(0,40),ylim=(6.6,-.6));ax.set_yticks(range(7),[f'{k} ({int(n)})' for k,n in zip(aa.index,aa.records)])
    ax.tick_params(axis='y',length=0,pad=3,labelsize=5.7);ax.spines['left'].set_visible(False)
    ax.set_xticks([0,10,20,30,40]);ax.tick_params(axis='x',labelsize=5.7)
    for i,row in enumerate(aa.itertuples()):
        ax.text(1.03,i,f'{row.saving_t/1000:.2f}',transform=ax.get_yaxis_transform(),fontsize=5.8,va='center')
    txt(f,104,159,'kt CO$_2$-eq yr$^{-1}$; parentheses: selected records',5.8)
    map_legend(f,167)
    line(f,3,183,180,183,lw=.5)
    panel(f,3,186,'g','Spatial concentration of OPT savings')
    ax=axis(f,28,195,77,16)
    ax.plot(rank['rank'],rank.cum_saving_pct,color=NAVY,lw=1.1)
    ax.set(xscale='log',xlim=(1,479),ylim=(0,103));ax.set_xticks([1,10,100,479],['1','10','100','479']);ax.minorticks_off()
    ax.set_yticks([0,50,100]);ax.tick_params(labelsize=5.7,length=2)
    ax.set_ylabel('Cumulative (%)',fontsize=5.7,labelpad=3)
    ax.set_xlabel('H3 cells ranked by benefit (log scale)',fontsize=5.8,labelpad=2)
    top=rank.loc[rank['rank'].eq(10),'cum_saving_pct'].iloc[0]
    ax.plot([10],[top],marker='o',markersize=2.7,color=NAVY)
    txt(f,117,194,f'Top 10 cells: {top:.1f}%',7,fontweight='bold')
    txt(f,117,201,'479 occupied cells ranked\nby descending OPT reduction',6,linespacing=1.5)
    audit_map_sizes(f,'FigS1_OPT_details');save(f,'FigS1_OPT_details')
