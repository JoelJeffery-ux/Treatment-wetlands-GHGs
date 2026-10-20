# CW greenhouse-gas figures

Python 3.11. Each figure folder contains a `plot.py` script. Matching data are
provided in the companion figshare archive.

## Installation and use

Place the extracted data and code folders in the same directory:

```text
working_folder/
  figshare_data/
  github_code/
```

From `github_code`, install the dependencies and run all figures:

```bash
pip install -r requirements.txt
python run_all.py
```

To run one figure or a selection:

```bash
python Fig2/plot.py
python run_all.py --only Fig1 Fig4 ED3
```

The options `--data PATH`, `--out PATH` and `--external-cache PATH` set alternative
data, output and cache directories. Each figure produces PNG, PDF and editable SVG
files in `reproduced_figures`.

## External inputs

Map and monitoring-climate inputs are downloaded from Natural Earth and WorldClim
to `external_cache`. For offline use, place `ne_110m_land.zip`,
`wc2.1_10m_bio_1.tif` and `wc2.1_10m_bio_12.tif` in that directory.
Source CSV files use UTF-8 with BOM and are compatible with Excel and pandas.

## Figure coverage

Fig1–Fig4 are the main figures, ED1–ED4 are Extended Data, and S01–S08 are
supplementary figures. S08 contains additional OPT details.
Shared plotting functions are in `common.py` and `_management_*.py`.

The scripts reconstruct figures from processed source data. Full model refitting
requires the system-level inputs held by the authors. Final manuscript layouts
were adjusted in Adobe Illustrator.

Code licence: MIT. External datasets retain their original licences.
