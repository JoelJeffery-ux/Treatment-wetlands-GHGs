"""Download and read external map and climate inputs."""
from pathlib import Path
import io, json, shutil, subprocess, urllib.request, zipfile
import numpy as np

NE='https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip'
WC='https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip'

def obtain(path,url):
    path=Path(path)
    if path.exists():return path
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_suffix(path.suffix+'.part')
    try:urllib.request.urlretrieve(url,partial)
    except OSError:
        curl=shutil.which('curl.exe') or shutil.which('curl')
        if not curl:raise
        subprocess.run([curl,'--fail','--location','--retry','2','--output',str(partial),url],check=True)
    partial.replace(path)
    return path

def load_land(cache):
    import shapefile
    arc=obtain(Path(cache)/'ne_110m_land.zip',NE)
    with zipfile.ZipFile(arc) as z:
        args={ext:io.BytesIO(z.read('ne_110m_land.'+ext)) for ext in ['shp','shx','dbf']}
        reader=shapefile.Reader(**args)
        return {'type':'FeatureCollection','features':[s.__geo_interface__ for s in reader.iterShapeRecords()]}

def monitoring_climate(locations,cache):
    """WorldClim v2.1 BIO1 is in degrees C; BIO12 is in mm."""
    import rasterio
    cache=Path(cache);files=[cache/f'wc2.1_10m_bio_{i}.tif' for i in [1,12]]
    if not all(p.exists() for p in files):
        arc=obtain(cache/'wc2.1_10m_bio.zip',WC)
        with zipfile.ZipFile(arc) as z:
            for p in files:
                if not p.exists():p.write_bytes(z.read(p.name))
    result=locations.copy()
    for path,col in zip(files,['mean_annual_temperature_C','annual_precipitation_mm']):
        with rasterio.open(path) as src:
            values=np.array([v[0] for v in src.sample(zip(locations.longitude_deg,locations.latitude_deg))],float)
            if src.nodata is not None:values[values==src.nodata]=np.nan
        result[col]=values
    if result[['mean_annual_temperature_C','annual_precipitation_mm']].isna().any().any():
        raise ValueError('Missing climate values at monitoring locations; inspect provider input.')
    return result
