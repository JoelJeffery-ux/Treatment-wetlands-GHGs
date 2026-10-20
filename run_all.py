"""Run the figure scripts against the matching figshare data folder."""
from pathlib import Path
import argparse,subprocess,sys
ROOT=Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=ROOT.parent/'figshare_data')
    ap.add_argument('--out',type=Path,default=ROOT.parent/'reproduced_figures')
    ap.add_argument('--external-cache',type=Path,default=ROOT.parent/'external_cache')
    ap.add_argument('--only',nargs='*',help='Optional figure IDs, e.g. Fig1 Fig2 ED3 S02')
    a=ap.parse_args()
    scripts=[ROOT/f'Fig{i}/plot.py' for i in range(1,5)]
    scripts += [ROOT/f'Extended_Data/ED{i}/plot.py' for i in range(1,5)]
    scripts += [ROOT/f'Supplementary/S{i:02d}/plot.py' for i in range(1,9)]
    for script in scripts:
        name=script.parent.name
        if a.only and name not in a.only:continue
        print('Plotting '+name,flush=True)
        subprocess.run([sys.executable,str(script),'--data',str(a.data.resolve()),
                        '--out',str(a.out.resolve()),'--external-cache',str(a.external_cache.resolve())],check=True)
    print('Completed requested figures:',a.out.resolve())
if __name__=='__main__':main()
