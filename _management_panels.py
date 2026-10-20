"""Plot removal constraints and management sensitivity results."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import _management_core as b

POL=['C','N','D','CN','OPT']
COL={'C':'#BA8D4B','N':'#728CB1','D':'#3E968A','CN':'#9380A9','OPT':'#355E76'}
INK='#202E38';MUTED='#657681';TEAL='#3E968A';OCHRE='#C38936';GREY='#A5AFB6'
SUPPLEMENT_META={
 'pollutant':('category','Pollutant defining the removal-rate panel: COD,TN,NH4N,TP.'),
 'n_higher':('count','Selected OPT records with removal > CU removal + 1e-10.'),
 'n_unchanged':('count','Selected OPT records with absolute removal change <= 1e-10.'),
 'n_lower':('count','Selected OPT records with removal < CU removal - 1e-10.'),
 'n_pass':('count','Selected OPT records satisfying the pollutant-specific 5% relative-loss threshold (tolerance 1e-10).'),
 'min_constraint_margin':('fraction','Minimum selected removal minus [CU removal - 0.05*max(CU removal,0)].'),
 'q':('percentile','Quantile used for upstream missing-input reconstruction: 25,50,75. Not a posterior or bootstrap probability.'),
 'tolerance':('percent','Maximum permitted relative deterioration in each pollutant removal rate: 0,2,5.'),
 'plan':('category','Fixed q50 OPT plan, reapplied without selecting a new candidate at other q values.'),
 'available_records':('count','Inventory configurations still evaluable under the alternative reconstructed input scenario.'),
 'unsupported_records':('count','Inventory configurations outside the upstream input-support rules under the alternative reconstruction.'),
 'water_failed_changed_records':('count','Changed configurations failing at least one water constraint among the evaluable changed configurations; do not treat as percent of all records.'),
 'saving_t_if_all_available':('t CO2-eq yr-1','Full fixed-plan saving available only when every inventory configuration can be evaluated. Missing value is unavailable, not zero.'),
 'available_records_saving_t':('t CO2-eq yr-1','Partial fixed-plan sum for available records. Not a complete total or a validated feasible-plan benefit; not plotted.')}

def supplement_data(core=b):
    long=pd.read_csv(core.DATA/'Supplementary/S06/removal_plot_points.csv')
    # Four independent plotted marginal distributions; rows do not link systems.
    columns={}
    for p,z in long.groupby('pollutant'):
        columns['base_removal_'+p]=z.CU_removal.to_numpy()
        columns['removal_'+p]=z.OPT_removal.to_numpy()
    water=pd.DataFrame(columns)
    summary=pd.read_csv(core.DATA/'Supplementary/S06/constraint_summary.csv')
    a=pd.read_csv(core.DATA/'Supplementary/S07/input_sensitivity.csv')
    c=pd.read_csv(core.DATA/'Supplementary/S07/water_sensitivity.csv')
    q=pd.concat([a,c]).drop_duplicates(['q','tolerance','policy'])
    fixed=pd.read_csv(core.DATA/'Supplementary/S07/fixed_plan_feasibility.csv')
    return water,summary,q,fixed

def water_constraints():
    w,s,_,_=supplement_data();f=b.figure(162)
    b.txt(f,8,9,'OPT selected records: n = 1,896; each pollutant evaluated separately',5.8)
    for i,p in enumerate(['COD','TN','NH4N','TP']):
        x=17+(i%2)*89;y=20+(i//2)*71
        title={'COD':'COD','TN':'TN','NH4N':'NH$_4^+$–N','TP':'TP'}[p]
        b.panel(f,x-9,y-17,'abcd'[i],title)
        ax=b.axis(f,x,y,65,48)
        old=100*w['base_removal_'+p];new=100*w['removal_'+p];diff=new-old
        xx=np.linspace(0,100,101)
        ax.plot(xx,xx,color=MUTED,lw=.65,ls=(0,(4,2)),zorder=1)
        ax.plot(xx,.95*xx,color=OCHRE,lw=.9,ls=(0,(1.5,1.2)),zorder=2)
        for flag,color in [(diff.abs().le(1e-8),GREY),(diff.gt(1e-8),TEAL),(diff.lt(-1e-8),OCHRE)]:
            ax.scatter(old[flag],new[flag],s=5.5,c=color,alpha=.40,edgecolors='none',rasterized=False,zorder=3)
        row=s[s.pollutant.eq(p)].iloc[0]
        ax.text(.035,.96,f'Higher {int(row.n_higher):,}  |  Unchanged {int(row.n_unchanged):,}\nLower {int(row.n_lower):,}  |  Passing {int(row.n_pass):,}',
            transform=ax.transAxes,va='top',fontsize=5.2,linespacing=1.5,color=INK)
        ax.set(xlim=(0,102),ylim=(0,102),xticks=[0,25,50,75,100],yticks=[0,25,50,75,100])
        ax.set_xlabel('CU removal (%)',fontsize=5.8,labelpad=2)
        ax.set_ylabel('OPT removal (%)',fontsize=5.8,labelpad=2)
        ax.tick_params(labelsize=5.5,pad=2)
    handles=[Line2D([],[],color=MUTED,lw=.7,ls=(0,(4,2)),label='Unchanged removal'),
        Line2D([],[],color=OCHRE,lw=.9,ls=(0,(1.5,1.2)),label='Maximum 5% relative loss')]
    f.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,1-149/162),ncol=2,frameon=False,fontsize=5.6,handlelength=3)
    b.txt(f,8,158,'Predicted / anchored removal rates; all selected records pass the relative constraint; absolute effluent limits are not tested.',5.1)
    b.save(f,'FigS2_water_constraints')

def sensitivity():
    _,_,q,fx=supplement_data();f=b.figure(170)
    b.panel(f,4,3,'a','Water-quality constraint')
    b.panel(f,96,3,'b','Reconstructed management inputs')
    b.txt(f,9,10,'q50 inputs; reoptimised at each tolerance',5.5)
    b.txt(f,101,10,'5% relative loss; reoptimised at each q',5.5)
    for col,(variable,subset,values,max_y) in enumerate([
        ('tolerance',q[q.q.eq(50)],[0,2,5],80),('q',q[q.tolerance.eq(5)],[25,50,75],145)]):
        ax=b.axis(f,18+col*91,22,64,48)
        for k in POL:
            rows=subset[subset.policy.eq(k)].set_index(variable).loc[values]
            yy=rows.saving_t.to_numpy()/1000
            ax.plot(values,yy,color=COL[k],lw=1.25 if k=='OPT' else .85,marker='o',ms=3 if k=='OPT' else 2,
                markeredgecolor='white',markeredgewidth=.35,label=k,zorder=5 if k=='OPT' else 3)
            if k=='OPT':
                for xv,yv in zip(values,yy):ax.annotate(f'{yv:.2f}',(xv,yv),xytext=(0,5),textcoords='offset points',ha='center',fontsize=5.1,color=COL[k])
        ax.set(ylim=(0,max_y),xticks=values)
        ax.set_xlim((-.4,5.4) if col==0 else (20,80))
        ax.set_xlabel('Maximum relative removal loss (%)' if col==0 else 'Input reconstruction quantile',fontsize=5.4,labelpad=2)
        if col:ax.set_xticklabels(['q25','q50','q75'])
        ax.set_ylabel('Avoided emissions (kt CO$_2$-eq yr$^{-1}$)',fontsize=5.5,labelpad=2)
        ax.tick_params(labelsize=5.4,pad=2)
        ax.set_yticks([0,20,40,60,80] if col==0 else [0,40,80,120])
    handles=[Line2D([],[],color=COL[k],lw=1.2,marker='o',ms=2.5,label=k) for k in POL]
    f.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,1-79/170),ncol=5,frameon=False,fontsize=5.5,handlelength=2)
    b.line(f,4,90,179,90,lw=.4)
    b.panel(f,4,94,'c','Fixed plan: outside input support')
    b.panel(f,96,94,'d','Fixed plan: water-constraint failures')
    b.txt(f,9,101,'All inventory configurations; n = 4,939',5.4)
    b.txt(f,101,101,'Changed configurations still evaluable',5.4)
    fx=fx.set_index('q').loc[[25,50,75]]
    for col,field in enumerate(['unsupported_records','water_failed_changed_records']):
        ax=b.axis(f,18+col*91,112,64,38)
        vals=fx[field].to_numpy()
        ax.bar([0,1,2],vals,width=.5,color=[OCHRE,GREY,OCHRE],zorder=3)
        for i,v in enumerate(vals):ax.text(i,v+(10 if col==0 else 3),f'{int(v):,}',ha='center',va='bottom',fontsize=6)
        ax.set(xticks=[0,1,2],xticklabels=['q25','q50','q75'],ylim=(0,550 if col==0 else 160))
        ax.set_ylabel('Configurations (n)',fontsize=5.6,labelpad=2)
        ax.set_xlabel('Input reconstruction quantile',fontsize=5.5,labelpad=2)
        ax.set_yticks([0,200,400] if col==0 else [0,50,100,150]);ax.tick_params(labelsize=5.4,pad=2)
    b.txt(f,4,165,'a,b: separately reoptimised scenarios, not confidence intervals. c,d: unchanged q50 OPT plan; different eligibility denominators.',5.1)
    b.save(f,'FigS3_sensitivity')
