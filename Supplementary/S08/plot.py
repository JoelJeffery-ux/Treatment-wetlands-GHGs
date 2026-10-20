"""Plot supplementary figure S08 from its source tables."""
from pathlib import Path
import sys,os
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'common.py').exists())
sys.path.insert(0,str(ROOT))
import common as cm
args=cm.setup('S08')
os.environ['CW_FIGURE_DATA']=str(args.data.resolve())
os.environ['CW_EXTERNAL_CACHE']=str(args.external_cache.resolve())
from _management_maps import detail
detail()
